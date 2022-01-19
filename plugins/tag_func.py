import logging
from typing import Iterator, Optional

import ida_name
import ida_funcs
import ida_idaapi
import ida_kernwin
import ida_dirtree

logger = logging.getLogger("tag_func")


def dirtree_find(dir, pattern) -> Iterator[ida_dirtree.dirtree_cursor_t]:
    """
    enumerate the matches for the given pattern against the given dirtree.
    this is just a Pythonic helper over the SWIG-generated routines.
    """
    # pattern format:
    #  "*" for all in current directory, does not recurse
    #  "/" for root directory
    #  "/sub_410000" for item by name
    #  "/foo" for directory by name, no trailing slash
    #  "/foo/*" for path prefix
    #      does not recurse beyond the prefix path
    #      matches "/foo/sub_401000" and but not "/foo/bar/sub_4010005"
    #  "/foo/sub_*" for path prefix (matches "/foo/sub_401000")
    #  "*main" for suffix (matches "/_main" because leading / is implied)
    #  "*mai*" for substring (matches "/_main" and "/_main_0" because leading / is implied)
    #
    #  wildcards only seem to match within path components
    #    does *not* work:
    #      "/*/sub_401000"
    #      "*/sub_401000"
    #      "*"
    #
    # to search by name, i guess use pattern "*" and check get_entry_name
    ff = ida_dirtree.dirtree_iterator_t()
    ok = dir.findfirst(ff, pattern)
    while ok:
        yield ff.cursor
        ok = dir.findnext(ff)


def dirtree_find_name(dir, name) -> Iterator[ida_dirtree.dirtree_cursor_t]:
    """
    given an item name
    find absolute paths with the name within the the given dirtree.
    this searches recursively.
    """
    directories = ["/"]

    while len(directories) > 0:
        directory = directories.pop(0)
        for cursor in dirtree_find(dir, f"{directory}*"):
            dirent = dir.resolve_cursor(cursor)

            if dir.get_entry_name(dirent) == name:
                yield cursor

            if dirent.isdir:
                abspath = dir.get_abspath(cursor)
                directories.append(f"{abspath}/")


def find_function_dirtree_path(va: int) -> Optional[str]:
    """
    given the address of a function
    find its absolute path within the function dirtree.
    """
    func_dir: ida_dirtree.dirtree_t = ida_dirtree.get_std_dirtree(ida_dirtree.DIRTREE_FUNCS)

    name = ida_name.get_name(va)
    if not name:
        return None

    for cursor in dirtree_find_name(func_dir, name):
        return func_dir.get_abspath(cursor)

    return None


def dirtree_mkdirs(dir, path):
    parts = path.split("/")

    for i in range(2, len(parts) + 1):
        prefix = "/".join(parts[:i])

        if not dir.isdir(prefix):
            e = dir.mkdir(prefix)
            if e != ida_dirtree.DTE_OK:
                logger.error("error: %s", ida_dirtree.dirtree_t_errstr(e))
                return e

    return ida_dirtree.DTE_OK


def main():
    va = ida_kernwin.get_screen_ea()
    f = ida_funcs.get_func(va)
    if not f:
        logger.error("function not found: 0x%x", va)
        return

    path = find_function_dirtree_path(f.start_ea)
    if not path:
        logger.error("function directory entry not found: 0x%x", f.start_ea)
        return

    func_dir: ida_dirtree.dirtree_t = ida_dirtree.get_std_dirtree(ida_dirtree.DIRTREE_FUNCS)

    dirent = func_dir.resolve_path(path)
    name = func_dir.get_entry_name(dirent)
    existing_tag = path[:-(len("/") + len(name))].lstrip("/")

    # ask_str(defval, hist, prompt) -> PyObject *
    # I'm not sure what "history id" does.
    tag = ida_kernwin.ask_str(existing_tag, 69, "tag:")
    if not tag:
        return

    tag_path = f"/{tag}"
    if not func_dir.isdir(tag_path):
        logger.info("creating tag: %s", tag)

        e = dirtree_mkdirs(func_dir, tag_path)
        if e != ida_dirtree.DTE_OK:
            logger.error("error: failed to create tag: %s", tag)
            return
 
    else:
        logger.debug("tag exists: %s", tag)

    src_path = path
    src_dirent = func_dir.resolve_path(src_path)
    src_name = func_dir.get_entry_name(src_dirent)

    dst_name = src_name
    dst_path = f"{tag_path}/{dst_name}"

    if src_path == dst_path:
        logger.info("skipping move to itself")
        return

    logger.info("moving %s from %s to %s", src_name, src_path, dst_path)
    e = func_dir.rename(src_path, dst_path)
    if e != ida_dirtree.DTE_OK:
        logger.error("error: %s", ida_dirtree.dirtree_t_errstr(e))
        return


class FunctionTagPlugin(ida_idaapi.plugin_t):
    # Mandatory definitions
    PLUGIN_NAME = "Function Tag"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_AUTHORS = "william.ballenthin@mandiant.com"

    wanted_name = PLUGIN_NAME
    wanted_hotkey = "Z"
    comment = "Quickly organize functions into tags via hotkey"
    version = ""
    flags = 0

    def __init__(self):
        """initialize plugin"""
        pass

    def init(self):
        """called when IDA is loading the plugin"""
        print("Function Tag: loaded")
        return ida_idaapi.PLUGIN_OK

    def term(self):
        """called when IDA is unloading the plugin"""
        pass

    def run(self, arg):
        """called when IDA is running the plugin as a script"""
        main()
        return True


def PLUGIN_ENTRY():
    return FunctionTagPlugin()


if __name__ == "__main__":
    main()
