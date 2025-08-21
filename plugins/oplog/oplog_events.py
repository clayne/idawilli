import logging
from typing import Any, Literal
from datetime import datetime

import ida_ua
import ida_funcs
import ida_range
import ida_segment
import ida_typeinf
from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)


class FuncModel(BaseModel):
    """Pydantic model for ida_funcs.func_t structure."""

    start_ea: int
    end_ea: int
    flags: int
    frame: int
    frsize: int
    frregs: int
    argsize: int
    fpd: int
    color: int
    pntqty: int
    regvarqty: int
    regargqty: int
    tailqty: int
    owner: int
    refqty: int
    name: str | None = None

    @classmethod
    def from_func_t(cls, func: ida_funcs.func_t) -> "FuncModel":
        """Create FuncModel from ida_funcs.func_t instance."""
        return cls(
            start_ea=func.start_ea,
            end_ea=func.end_ea,
            flags=func.flags,
            frame=func.frame,
            frsize=func.frsize,
            frregs=func.frregs,
            argsize=func.argsize,
            fpd=func.fpd,
            color=func.color,
            pntqty=func.pntqty,
            regvarqty=func.regvarqty,
            regargqty=func.regargqty,
            tailqty=func.tailqty,
            owner=func.owner,
            refqty=func.refqty,
            name=func.get_name() if hasattr(func, "get_name") else None,
        )


class OpModel(BaseModel):
    """Pydantic model for ida_ua.op_t structure."""

    n: int
    type: int
    offb: int
    offo: int
    flags: int
    dtype: int
    reg: int
    phrase: int
    value: int
    addr: int
    specval: int
    specflag1: int
    specflag2: int
    specflag3: int
    specflag4: int

    @classmethod
    def from_op_t(cls, op: ida_ua.op_t) -> "OpModel":
        """Create OpModel from ida_ua.op_t instance."""
        return cls(
            n=op.n,
            type=op.type,
            offb=op.offb,
            offo=op.offo,
            flags=op.flags,
            dtype=op.dtype,
            reg=op.reg,
            phrase=op.phrase,
            value=op.value,
            addr=op.addr,
            specval=op.specval,
            specflag1=op.specflag1,
            specflag2=op.specflag2,
            specflag3=op.specflag3,
            specflag4=op.specflag4,
        )


class InsnModel(BaseModel):
    """Pydantic model for ida_ua.insn_t structure."""

    cs: int
    ip: int
    ea: int
    itype: int
    size: int
    auxpref: int
    auxpref_u16: list[int]
    auxpref_u8: list[int]
    segpref: int
    insnpref: int
    flags: int
    ops: list[OpModel]

    @classmethod
    def from_insn_t(cls, insn: ida_ua.insn_t) -> "InsnModel":
        """Create InsnModel from ida_ua.insn_t instance."""
        return cls(
            cs=insn.cs,
            ip=insn.ip,
            ea=insn.ea,
            itype=insn.itype,
            size=insn.size,
            auxpref=insn.auxpref,
            auxpref_u16=list(insn.auxpref_u16),
            auxpref_u8=list(insn.auxpref_u8),
            segpref=insn.segpref,
            insnpref=insn.insnpref,
            flags=insn.flags,
            ops=[OpModel.from_op_t(insn.ops[i]) for i in range(8)],
        )


class SegmentModel(BaseModel):
    """Pydantic model for ida_segment.segment_t structure."""

    start_ea: int
    end_ea: int
    name: int
    sclass: int
    orgbase: int
    align: int
    comb: int
    perm: int
    bitness: int
    flags: int
    sel: int
    defsr: list[int]
    type: int
    color: int
    segment_name: str | None = None
    segment_class: str | None = None

    @field_validator("bitness")
    @classmethod
    def validate_bitness(cls, v: int) -> int:
        """Validate bitness is in range 0-2."""
        if v not in (0, 1, 2):
            raise ValueError("bitness must be 0 (16bit), 1 (32bit), or 2 (64bit)")
        return v

    @field_validator("defsr")
    @classmethod
    def validate_defsr_length(cls, v: list[int]) -> list[int]:
        """Validate defsr list has exactly 16 elements."""
        if len(v) != 16:
            raise ValueError(f"defsr must have exactly 16 elements, got {len(v)}")
        return v

    @field_validator("align")
    @classmethod
    def validate_align(cls, v: int) -> int:
        """Validate align is in range 0-255."""
        if not (0 <= v <= 255):
            raise ValueError(f"align must be in range 0-255, got {v}")
        return v

    @field_validator("comb")
    @classmethod
    def validate_comb(cls, v: int) -> int:
        """Validate comb is in range 0-255."""
        if not (0 <= v <= 255):
            raise ValueError(f"comb must be in range 0-255, got {v}")
        return v

    @field_validator("perm")
    @classmethod
    def validate_perm(cls, v: int) -> int:
        """Validate perm is in range 0-255."""
        if not (0 <= v <= 255):
            raise ValueError(f"perm must be in range 0-255, got {v}")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: int) -> int:
        """Validate type is in range 0-255."""
        if not (0 <= v <= 255):
            raise ValueError(f"type must be in range 0-255, got {v}")
        return v

    @field_validator("flags")
    @classmethod
    def validate_flags(cls, v: int) -> int:
        """Validate flags is in range 0-65535."""
        if not (0 <= v <= 65535):
            raise ValueError(f"flags must be in range 0-65535, got {v}")
        return v

    @classmethod
    def from_segment_t(cls, segment: ida_segment.segment_t) -> "SegmentModel":
        """Create SegmentModel from ida_segment.segment_t instance."""
        # Convert defsr array to list
        defsr_list = [segment.defsr[i] for i in range(16)]

        return cls(
            start_ea=segment.start_ea,
            end_ea=segment.end_ea,
            name=segment.name,
            sclass=segment.sclass,
            orgbase=segment.orgbase,
            align=segment.align,
            comb=segment.comb,
            perm=segment.perm,
            bitness=segment.bitness,
            flags=segment.flags,
            sel=segment.sel,
            defsr=defsr_list,
            type=segment.type,
            color=segment.color,
            segment_name=ida_segment.get_segm_name(segment) if segment else None,
            segment_class=ida_segment.get_segm_class(segment) if segment else None,
        )


class RangeModel(BaseModel):
    """Pydantic model for ida_range.range_t structure."""

    start_ea: int
    end_ea: int

    @classmethod
    def from_range_t(cls, range_obj: ida_range.range_t) -> "RangeModel":
        """Create RangeModel from ida_range.range_t instance.

        Args:
            range_obj: The range_t instance to convert.

        Returns:
            RangeModel instance with populated attributes.
        """
        return cls(
            start_ea=range_obj.start_ea,
            end_ea=range_obj.end_ea,
        )


class UdmModel(BaseModel):
    """Pydantic model for ida_typeinf.udm_t structure."""

    offset: int
    size: int
    name: str
    cmt: str
    tid: int  # from udm.type.get_tid()
    repr: str
    effalign: int
    tafld_bits: int
    fda: int

    @classmethod
    def from_udm_t(cls, udm: ida_typeinf.udm_t) -> "UdmModel":
        return cls(
            offset=udm.offset,
            size=udm.size,
            name=udm.name,
            cmt=udm.cmt,
            tid=udm.type.get_tid(),
            repr=str(udm.repr),
            effalign=udm.effalign,
            tafld_bits=udm.tafld_bits,
            fda=udm.fda,
        )


class EdmModel(BaseModel):
    """Pydantic model for ida_typeinf.edm_t structure."""

    name: str
    comment: str
    value: int
    tid: int

    @classmethod
    def from_edm_t(cls, edm: ida_typeinf.edm_t) -> "EdmModel":
        name = edm.name
        comment = edm.cmt
        value = edm.value
        tid = edm.get_tid()

        return cls(
            name=name,
            comment=comment,
            value=value,
            tid=tid,
        )


class adding_segm_event(BaseModel):
    event_name: Literal["adding_segm"]
    timestamp: datetime
    s: SegmentModel


class segm_added_event(BaseModel):
    event_name: Literal["segm_added"]
    timestamp: datetime
    s: SegmentModel


class deleting_segm_event(BaseModel):
    event_name: Literal["deleting_segm"]
    timestamp: datetime
    start_ea: int


class segm_deleted_event(BaseModel):
    event_name: Literal["segm_deleted"]
    timestamp: datetime
    start_ea: int
    end_ea: int
    flags: int


class changing_segm_start_event(BaseModel):
    event_name: Literal["changing_segm_start"]
    timestamp: datetime
    s: SegmentModel
    new_start: int
    segmod_flags: int


class segm_start_changed_event(BaseModel):
    event_name: Literal["segm_start_changed"]
    timestamp: datetime
    s: SegmentModel
    oldstart: int


class changing_segm_end_event(BaseModel):
    event_name: Literal["changing_segm_end"]
    timestamp: datetime
    s: SegmentModel
    new_end: int
    segmod_flags: int


class segm_end_changed_event(BaseModel):
    event_name: Literal["segm_end_changed"]
    timestamp: datetime
    s: SegmentModel
    oldend: int


class changing_segm_name_event(BaseModel):
    event_name: Literal["changing_segm_name"]
    timestamp: datetime
    s: SegmentModel
    oldname: str


class segm_name_changed_event(BaseModel):
    event_name: Literal["segm_name_changed"]
    timestamp: datetime
    s: SegmentModel
    name: str


class changing_segm_class_event(BaseModel):
    event_name: Literal["changing_segm_class"]
    timestamp: datetime
    s: SegmentModel


class segm_class_changed_event(BaseModel):
    event_name: Literal["segm_class_changed"]
    timestamp: datetime
    s: SegmentModel
    sclass: str


class segm_attrs_updated_event(BaseModel):
    event_name: Literal["segm_attrs_updated"]
    timestamp: datetime
    s: SegmentModel


class segm_moved_event(BaseModel):
    event_name: Literal["segm_moved"]
    timestamp: datetime
    _from: int
    to: int
    size: int
    changed_netmap: bool


class allsegs_moved_event(BaseModel):
    event_name: Literal["allsegs_moved"]
    timestamp: datetime
    info: Any


class func_added_event(BaseModel):
    event_name: Literal["func_added"]
    timestamp: datetime
    pfn: FuncModel


class func_updated_event(BaseModel):
    event_name: Literal["func_updated"]
    timestamp: datetime
    pfn: FuncModel


class set_func_start_event(BaseModel):
    event_name: Literal["set_func_start"]
    timestamp: datetime
    pfn: FuncModel
    new_start: int


class set_func_end_event(BaseModel):
    event_name: Literal["set_func_end"]
    timestamp: datetime
    pfn: FuncModel
    new_end: int


class deleting_func_event(BaseModel):
    event_name: Literal["deleting_func"]
    timestamp: datetime
    pfn: FuncModel


class func_deleted_event(BaseModel):
    event_name: Literal["func_deleted"]
    timestamp: datetime
    func_ea: int


class thunk_func_created_event(BaseModel):
    event_name: Literal["thunk_func_created"]
    timestamp: datetime
    pfn: FuncModel


class func_tail_appended_event(BaseModel):
    event_name: Literal["func_tail_appended"]
    timestamp: datetime
    pfn: FuncModel
    tail: FuncModel


class deleting_func_tail_event(BaseModel):
    event_name: Literal["deleting_func_tail"]
    timestamp: datetime
    pfn: FuncModel
    tail: RangeModel


class func_tail_deleted_event(BaseModel):
    event_name: Literal["func_tail_deleted"]
    timestamp: datetime
    pfn: FuncModel
    tail_ea: int


class tail_owner_changed_event(BaseModel):
    event_name: Literal["tail_owner_changed"]
    timestamp: datetime
    tail: FuncModel
    owner_func: int
    old_owner: int


class func_noret_changed_event(BaseModel):
    event_name: Literal["func_noret_changed"]
    timestamp: datetime
    pfn: FuncModel


class updating_tryblks_event(BaseModel):
    event_name: Literal["updating_tryblks"]
    timestamp: datetime
    tbv: Any


class tryblks_updated_event(BaseModel):
    event_name: Literal["tryblks_updated"]
    timestamp: datetime
    tbv: Any


class deleting_tryblks_event(BaseModel):
    event_name: Literal["deleting_tryblks"]
    timestamp: datetime
    range: RangeModel


class changing_cmt_event(BaseModel):
    event_name: Literal["changing_cmt"]
    timestamp: datetime
    ea: int
    repeatable_cmt: bool
    # TODO: add existing comment
    newcmt: str


class cmt_changed_event(BaseModel):
    event_name: Literal["cmt_changed"]
    timestamp: datetime
    ea: int
    # TODO: add the new comment string
    repeatable_cmt: bool


class changing_range_cmt_event(BaseModel):
    event_name: Literal["changing_range_cmt"]
    timestamp: datetime
    kind: Any
    a: RangeModel
    cmt: str
    repeatable: bool


class range_cmt_changed_event(BaseModel):
    event_name: Literal["range_cmt_changed"]
    timestamp: datetime
    kind: Any
    a: RangeModel
    cmt: str
    repeatable: bool


class extra_cmt_changed_event(BaseModel):
    event_name: Literal["extra_cmt_changed"]
    timestamp: datetime
    ea: int
    line_idx: int
    cmt: str


class sgr_changed_event(BaseModel):
    event_name: Literal["sgr_changed"]
    timestamp: datetime
    start_ea: int
    end_ea: int
    regnum: int
    value: Any
    old_value: Any
    tag: int


class sgr_deleted_event(BaseModel):
    event_name: Literal["sgr_deleted"]
    timestamp: datetime
    start_ea: int
    end_ea: int
    regnum: int


class make_code_event(BaseModel):
    event_name: Literal["make_code"]
    timestamp: datetime
    insn: InsnModel


class make_data_event(BaseModel):
    event_name: Literal["make_data"]
    timestamp: datetime
    ea: int
    flags: int
    tid: int
    len: int


class destroyed_items_event(BaseModel):
    event_name: Literal["destroyed_items"]
    timestamp: datetime
    ea1: int
    ea2: int
    will_disable_range: bool


class renamed_event(BaseModel):
    event_name: Literal["renamed"]
    timestamp: datetime
    ea: int
    new_name: str
    local_name: bool
    old_name: str


class byte_patched_event(BaseModel):
    event_name: Literal["byte_patched"]
    timestamp: datetime
    ea: int
    old_value: int


class item_color_changed_event(BaseModel):
    event_name: Literal["item_color_changed"]
    timestamp: datetime
    ea: int
    color: Any


class callee_addr_changed_event(BaseModel):
    event_name: Literal["callee_addr_changed"]
    timestamp: datetime
    ea: int
    callee: int


class bookmark_changed_event(BaseModel):
    event_name: Literal["bookmark_changed"]
    timestamp: datetime
    index: int
    ea: int
    desc: str
    operation: int


class changing_op_type_event(BaseModel):
    event_name: Literal["changing_op_type"]
    timestamp: datetime
    ea: int
    n: int
    opinfo: Any


class op_type_changed_event(BaseModel):
    event_name: Literal["op_type_changed"]
    timestamp: datetime
    ea: int
    n: int


class dirtree_mkdir_event(BaseModel):
    event_name: Literal["dirtree_mkdir"]
    timestamp: datetime
    path: str


class dirtree_rmdir_event(BaseModel):
    event_name: Literal["dirtree_rmdir"]
    timestamp: datetime
    path: str


class dirtree_link_event(BaseModel):
    event_name: Literal["dirtree_link"]
    timestamp: datetime
    path: str
    link: bool


class dirtree_move_event(BaseModel):
    event_name: Literal["dirtree_move"]
    timestamp: datetime
    _from: str
    to: str


class dirtree_rank_event(BaseModel):
    event_name: Literal["dirtree_rank"]
    timestamp: datetime
    path: str
    rank: int


class dirtree_rminode_event(BaseModel):
    event_name: Literal["dirtree_rminode"]
    timestamp: datetime
    inode: int


class dirtree_segm_moved_event(BaseModel):
    event_name: Literal["dirtree_segm_moved"]
    timestamp: datetime


class changing_ti_event(BaseModel):
    event_name: Literal["changing_ti"]
    timestamp: datetime
    ea: int
    # TODO add existing TI
    new_type: Any
    new_fnames: Any


class ti_changed_event(BaseModel):
    event_name: Literal["ti_changed"]
    timestamp: datetime
    ea: int
    type: Any
    fnames: Any


class changing_op_ti_event(BaseModel):
    event_name: Literal["changing_op_ti"]
    timestamp: datetime
    ea: int
    n: int
    new_type: Any
    new_fnames: Any


class op_ti_changed_event(BaseModel):
    event_name: Literal["op_ti_changed"]
    timestamp: datetime
    ea: int
    n: int
    type: Any
    fnames: Any


class local_types_changed_event(BaseModel):
    event_name: Literal["local_types_changed"]
    timestamp: datetime
    ltc: Any
    ordinal: int
    name: str


class lt_udm_created_event(BaseModel):
    event_name: Literal["lt_udm_created"]
    timestamp: datetime
    udtname: str
    udm: UdmModel


class lt_udm_deleted_event(BaseModel):
    event_name: Literal["lt_udm_deleted"]
    timestamp: datetime
    udtname: str
    udm_tid: int
    udm: UdmModel


class lt_udm_renamed_event(BaseModel):
    event_name: Literal["lt_udm_renamed"]
    timestamp: datetime
    udtname: str
    udm: UdmModel
    oldname: str


class lt_udm_changed_event(BaseModel):
    event_name: Literal["lt_udm_changed"]
    timestamp: datetime
    udtname: str
    udm_tid: int
    udmold: UdmModel
    udmnew: UdmModel


class lt_udt_expanded_event(BaseModel):
    event_name: Literal["lt_udt_expanded"]
    timestamp: datetime
    udtname: str
    udm_tid: int
    delta: int


class lt_edm_created_event(BaseModel):
    event_name: Literal["lt_edm_created"]
    timestamp: datetime
    enumname: str
    edm: EdmModel


class lt_edm_deleted_event(BaseModel):
    event_name: Literal["lt_edm_deleted"]
    timestamp: datetime
    enumname: str
    edm_tid: int
    edm: EdmModel


class lt_edm_renamed_event(BaseModel):
    event_name: Literal["lt_edm_renamed"]
    timestamp: datetime
    enumname: str
    edm: EdmModel
    oldname: str


class lt_edm_changed_event(BaseModel):
    event_name: Literal["lt_edm_changed"]
    timestamp: datetime
    enumname: str
    edm_tid: int
    edmold: EdmModel
    edmnew: EdmModel


class stkpnts_changed_event(BaseModel):
    event_name: Literal["stkpnts_changed"]
    timestamp: datetime
    pfn: FuncModel


class frame_created_event(BaseModel):
    event_name: Literal["frame_created"]
    timestamp: datetime
    func_ea: int


class frame_expanded_event(BaseModel):
    event_name: Literal["frame_expanded"]
    timestamp: datetime
    func_ea: int
    udm_tid: int
    delta: int


class frame_deleted_event(BaseModel):
    event_name: Literal["frame_deleted"]
    timestamp: datetime
    pfn: FuncModel


class frame_udm_created_event(BaseModel):
    event_name: Literal["frame_udm_created"]
    timestamp: datetime
    func_ea: int
    udm: UdmModel


class frame_udm_deleted_event(BaseModel):
    event_name: Literal["frame_udm_deleted"]
    timestamp: datetime
    func_ea: int
    udm_tid: int
    udm: UdmModel


class frame_udm_renamed_event(BaseModel):
    event_name: Literal["frame_udm_renamed"]
    timestamp: datetime
    func_ea: int
    udm: UdmModel
    oldname: str


class frame_udm_changed_event(BaseModel):
    event_name: Literal["frame_udm_changed"]
    timestamp: datetime
    func_ea: int
    udm_tid: int
    udmold: UdmModel
    udmnew: UdmModel


class determined_main_event(BaseModel):
    event_name: Literal["determined_main"]
    timestamp: datetime
    main: int


class extlang_changed_event(BaseModel):
    event_name: Literal["extlang_changed"]
    timestamp: datetime
    kind: int
    el: Any
    idx: int


class idasgn_matched_ea_event(BaseModel):
    event_name: Literal["idasgn_matched_ea"]
    timestamp: datetime
    ea: int
    name: str
    lib_name: str


idb_event = (
    renamed_event
    | make_code_event
    | make_data_event
    | func_added_event
    | segm_added_event
    | segm_moved_event
    | ti_changed_event
    | adding_segm_event
    | changing_ti_event
    | cmt_changed_event
    | sgr_changed_event
    | sgr_deleted_event
    | byte_patched_event
    | changing_cmt_event
    | dirtree_link_event
    | dirtree_move_event
    | dirtree_rank_event
    | func_deleted_event
    | func_updated_event
    | segm_deleted_event
    | set_func_end_event
    | allsegs_moved_event
    | deleting_func_event
    | deleting_segm_event
    | dirtree_mkdir_event
    | dirtree_rmdir_event
    | frame_created_event
    | frame_deleted_event
    | op_ti_changed_event
    | changing_op_ti_event
    | frame_expanded_event
    | lt_edm_changed_event
    | lt_edm_created_event
    | lt_edm_deleted_event
    | lt_edm_renamed_event
    | lt_udm_changed_event
    | lt_udm_created_event
    | lt_udm_deleted_event
    | lt_udm_renamed_event
    | set_func_start_event
    | destroyed_items_event
    | determined_main_event
    | dirtree_rminode_event
    | extlang_changed_event
    | lt_udt_expanded_event
    | op_type_changed_event
    | stkpnts_changed_event
    | tryblks_updated_event
    | bookmark_changed_event
    | changing_op_type_event
    | deleting_tryblks_event
    | segm_end_changed_event
    | updating_tryblks_event
    | changing_segm_end_event
    | extra_cmt_changed_event
    | frame_udm_changed_event
    | frame_udm_created_event
    | frame_udm_deleted_event
    | frame_udm_renamed_event
    | func_tail_deleted_event
    | idasgn_matched_ea_event
    | range_cmt_changed_event
    | segm_name_changed_event
    | changing_range_cmt_event
    | changing_segm_name_event
    | deleting_func_tail_event
    | dirtree_segm_moved_event
    | func_noret_changed_event
    | func_tail_appended_event
    | item_color_changed_event
    | segm_attrs_updated_event
    | segm_class_changed_event
    | segm_start_changed_event
    | tail_owner_changed_event
    | thunk_func_created_event
    | callee_addr_changed_event
    | changing_segm_class_event
    | changing_segm_start_event
    | local_types_changed_event
)
