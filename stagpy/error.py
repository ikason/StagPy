"""Exceptions raised by StagPy."""


class StagpyError(Exception):

    """Base class for exceptions raised by StagPy.

    Note:
        All exceptions derive from this class. To catch any error that might be
        raised by StagPy due to invalid requests/missing data, you only need to
        catch this exception.
    """

    pass


class ConfigSectionError(StagpyError):

    """Raised when invalid config section is requested."""

    def __init__(self, section):
        """Initialization of instances:

        Args:
            section (str): invalid section name.

        Attributes:
            section (str): invalid section name.
        """
        self.section = section
        super().__init__('invalid section name: {}'.format(section))


class ConfigOptionError(StagpyError):

    """Raised when invalid config option is requested."""

    def __init__(self, option):
        """Initialization of instances:

        Args:
            option (str): invalid option name.

        Attributes:
            option (str): invalid option name.
        """
        self.option = option
        super().__init__('invalid option name: {}'.format(option))


class NoSnapshotError(StagpyError):

    """Raised when no snapshot can be found."""

    def __init__(self, sdat):
        """Initialization of instances:

        Args:
            sdat (:class:`~stagpy.stagyydata.StagyyData`): the StagyyData
                instance for which no snapshot were found.

        Attributes:
            sdat (:class:`~stagpy.stagyydata.StagyyData`): the StagyyData
                instance for which no snapshot were found.
        """
        self.sdat = sdat
        super().__init__('no snapshot found for {}'.format(sdat))


class NoParFileError(StagpyError):

    """Raised when no par file can be found."""

    def __init__(self, parfile):
        """Initialization of instances:

        Args:
            parfile (pathlike): the expected path of
                the par file.

        Attributes:
            parfile (pathlike): the expected path of the par file.
        """
        self.parfile = parfile
        super().__init__('{} file not found'.format(parfile))


class NotAvailableError(StagpyError):

    """Raised when a feature is not available yet."""

    pass


class ParsingError(StagpyError):

    """Raised when a parsing error occurs."""

    def __init__(self, faulty_file, msg):
        """Initialization of instances:

        Args:
            faulty_file (pathlike): path of the file where a parsing problem
                was encountered.
            msg (str): error message.

        Attributes:
            file (pathlike): path of the file where a parsing problem was
                encountered.
            msg (str): error message.
        """
        self.file = faulty_file
        self.msg = msg
        super().__init__(faulty_file, msg)


class InvalidTimestepError(StagpyError):

    """Raised when invalid time step is requested."""

    def __init__(self, sdat, istep, msg):
        """Initialization of instances:

        Args:
            sdat (:class:`~stagpy.stagyydata.StagyyData`): the StagyyData
                instance for which the request was made.
            istep (int): the invalid time step index.
            msg (str): the error message.

        Attributes:
            sdat (:class:`~stagpy.stagyydata.StagyyData`): the StagyyData
                instance for which the request was made.
            istep (int): the invalid time step index.
            msg (str): the error message.
        """
        self.sdat = sdat
        self.istep = istep
        self.msg = msg
        super().__init__(sdat, istep, msg)


class InvalidZoomError(StagpyError):

    """Raised when invalid zoom is requested."""

    def __init__(self, zoom):
        """Initialization of instances:

        Args:
            zoom (int): the invalid zoom level.

        Attributes:
            zoom (int): the invalid zoom level.
        """
        self.zoom = zoom
        super().__init__('Zoom angle should be in [0,360] (received {})'
                         .format(zoom))


class StagnantLidError(StagpyError):

    """Raised when unexpected stagnant lid regime is found."""

    def __init__(self, sdat):
        """Initialization of instances:

        Args:
            sdat (:class:`~stagpy.stagyydata.StagyyData`): the StagyyData
                instance for which a stagnant lid regime was found.

        Attributes:
            sdat (:class:`~stagpy.stagyydata.StagyyData`): the StagyyData
                instance for which a stagnant lid regime was found.
        """
        self.sdat = sdat
        super().__init__('Stagnant lid regime for {}'.format(sdat))


class UnknownVarError(StagpyError):

    """Raised when invalid var is requested."""

    def __init__(self, varname):
        """Initialization of instances:

        Args:
            varname (str): the invalid var name.

        Attributes:
            varname (str): the invalid var name.
        """
        self.varname = varname
        super().__init__(varname)


class UnknownFieldVarError(UnknownVarError):

    """Raised when invalid field var is requested.

    Derived from :class:`~stagpy.error.UnknownVarError`.
    """

    pass


class UnknownRprofVarError(UnknownVarError):

    """Raised when invalid rprof var is requested.

    Derived from :class:`~stagpy.error.UnknownVarError`.
    """

    pass


class UnknownTimeVarError(UnknownVarError):

    """Raised when invalid time var is requested.

    Derived from :class:`~stagpy.error.UnknownVarError`.
    """

    pass
