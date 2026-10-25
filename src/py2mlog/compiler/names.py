from py2mlog.mlog.mlog_expressions import MlogVar

PREFIX_TMP = "__p2m_tmp"
PREFIX_LABEL = "__p2m_label"
PREFIX_FUNC_ARG = "__p2m_func_arg_"  # scoped


NAME_FUNC_RET_VAL = "__p2m_func_ret_val"  # scoped
NAME_FUNC_RET_ADDR = "__p2m_func_ret_addr"


VAR_ERR_MSG = MlogVar("__p2m_msg_err")


# maybe update this later, after making tests resistant to var name changes
GLOBAL_SCOPE = ""
PREFIX_FUNC_SCOPE = "__p2m_func_scope_"
