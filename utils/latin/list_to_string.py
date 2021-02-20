# file mygame/utils/latin/list_to_string.py

"""
This is adapted from the utility living in the main evennia directory
in order to accommodate Latin language things; maybe eventually we
can get "-que" to work here.
"""

def list_to_string(inlist, endsep="et", addquote=False):
    """
    This pretty-formats a list as string output, adding an optional
    alternative separator to the second to last entry.  If `addquote`
    is `True`, the outgoing strings will be surrounded by quotes.

    Args:
        inlist (list): The list to print.
        endsep (str, optional): If set, the last item separator will
            be replaced with this value.
        addquote (bool, optional): This will surround all outgoing
            values with double quotes.

    Returns:
        liststr (str): The list represented as a string.

    Examples:

        ```python
            # no endsep:
            [1,2,3] -> '1, 2, 3'
            # with endsep=='and':
            [1,2,3] -> '1, 2 and 3'
            # with addquote and endsep
            [1,2,3] -> '"1", "2" and "3"'
        ```

    """
    if not endsep:
        endsep = ","
    else:
        endsep = " " + endsep
    if not inlist:
        return ""
    if addquote:
        if len(inlist) == 1:
            return '"%s"' % inlist[0]
        return ", ".join('"%s"' % v for v in inlist[:-1]) + "%s %s" % (endsep, '"%s"' % inlist[-1])
    else:
        if len(inlist) == 1:
            return str(inlist[0])
        return ", ".join(str(v) for v in inlist[:-1]) + "%s %s" % (endsep, inlist[-1])
