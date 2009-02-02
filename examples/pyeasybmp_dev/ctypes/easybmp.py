import sys
import ctypes
import cpptypes
import ctypes_utils

easybmplib = cpptypes.AnyDLL( r"easybmp.dll" )

easybmplib.undecorated_names = {#mapping between decorated and undecorated names
    "unsigned short FlipWORD(unsigned short)" : "?FlipWORD@@YAGG@Z",
    "BMP::BMP(void)" : "??0BMP@@QAE@XZ",
    "bool BMP::SetPixel(int,int RGBApixel)" : "?SetPixel@BMP@@QAE_NHHURGBApixel@@@Z",
    "bool BMP::Read32bitRow(unsigned char *,int,int)" : "?Read32bitRow@BMP@@AAE_NPAEHH@Z",
    "bool BMP::ReadFromFile(char const *)" : "?ReadFromFile@BMP@@QAE_NPBD@Z",
    "void BMIH::display(void)" : "?display@BMIH@@QAEXXZ",
    "double Square(double)" : "?Square@@YANN@Z",
    "unsigned char BMP::FindClosestColor RGBApixel &)" : "?FindClosestColor@BMP@@AAEEAAURGBApixel@@@Z",
    "bool BMP::Read24bitRow(unsigned char *,int,int)" : "?Read24bitRow@BMP@@AAE_NPAEHH@Z",
    "int BMP::TellBitDepth(void)" : "?TellBitDepth@BMP@@QAEHXZ",
    "bool BMP::Write24bitRow(unsigned char *,int,int)" : "?Write24bitRow@BMP@@AAE_NPAEHH@Z",
    "BMIH::BMIH(void)" : "??0BMIH@@QAE@XZ",
    "int BMP::TellWidth(void)" : "?TellWidth@BMP@@QAEHXZ",
    "bool BMP::Write1bitRow(unsigned char *,int,int)" : "?Write1bitRow@BMP@@AAE_NPAEHH@Z",
    "RGBApixel & RGBApixel::operator= RGBApixel const &)" : "??4RGBApixel@@QAEAAU0@ABU0@@Z",
    "int BMP::TellVerticalDPI(void)" : "?TellVerticalDPI@BMP@@QAEHXZ",
    "bool BMP::WriteToFile(char const *)" : "?WriteToFile@BMP@@QAE_NPBD@Z",
    "bool BMP::Read4bitRow(unsigned char *,int,int)" : "?Read4bitRow@BMP@@AAE_NPAEHH@Z",
    "void BMP::SetDPI(int,int)" : "?SetDPI@BMP@@QAEXHH@Z",
    "int IntSquare(int)" : "?IntSquare@@YAHH@Z",
    "bool BMP::Write32bitRow(unsigned char *,int,int)" : "?Write32bitRow@BMP@@AAE_NPAEHH@Z",
    "BMFH & BMFH::operator= BMFH const &)" : "??4BMFH@@QAEAAV0@ABV0@@Z",
    "bool BMP::Read1bitRow(unsigned char *,int,int)" : "?Read1bitRow@BMP@@AAE_NPAEHH@Z",
    "BMFH::BMFH(void)" : "??0BMFH@@QAE@XZ",
    "BMP::BMP BMP &)" : "??0BMP@@QAE@AAV0@@Z",
    "bool BMP::Write4bitRow(unsigned char *,int,int)" : "?Write4bitRow@BMP@@AAE_NPAEHH@Z",
    "unsigned int FlipDWORD(unsigned int)" : "?FlipDWORD@@YAII@Z",
    "int BMP::TellHeight(void)" : "?TellHeight@BMP@@QAEHXZ",
    "bool IsBigEndian(void)" : "?IsBigEndian@@YA_NXZ",
    "RGBApixel BMP::GetPixel(int,int)const" : "?GetPixel@BMP@@QBE?AURGBApixel@@HH@Z",
    "bool BMP::SetBitDepth(int)" : "?SetBitDepth@BMP@@QAE_NH@Z",
    "void BMIH::SwitchEndianess(void)" : "?SwitchEndianess@BMIH@@QAEXXZ",
    "int BMP::TellNumberOfColors(void)" : "?TellNumberOfColors@BMP@@QAEHXZ",
    "BMP & BMP::operator= BMP const &)" : "??4BMP@@QAEAAV0@ABV0@@Z",
    "bool BMP::SetColor(int RGBApixel)" : "?SetColor@BMP@@QAE_NHURGBApixel@@@Z",
    "void BMFH::SwitchEndianess(void)" : "?SwitchEndianess@BMFH@@QAEXXZ",
    "void BMFH::display(void)" : "?display@BMFH@@QAEXXZ",
    "bool BMP::SetSize(int,int)" : "?SetSize@BMP@@QAE_NHH@Z",
    "bool BMP::Read8bitRow(unsigned char *,int,int)" : "?Read8bitRow@BMP@@AAE_NPAEHH@Z",
    "BMIH & BMIH::operator= BMIH const &)" : "??4BMIH@@QAEAAV0@ABV0@@Z",
    "bool BMP::Write8bitRow(unsigned char *,int,int)" : "?Write8bitRow@BMP@@AAE_NPAEHH@Z",
    "BMP::~BMP(void)" : "??1BMP@@QAE@XZ",
    "RGBApixel * BMP::operator()(int,int)" : "??RBMP@@QAEPAURGBApixel@@HH@Z",
    "RGBApixel BMP::GetColor(int)" : "?GetColor@BMP@@QAE?AURGBApixel@@H@Z",
    "int BMP::TellHorizontalDPI(void)" : "?TellHorizontalDPI@BMP@@QAEHXZ",
    "bool BMP::CreateStandardColorTable(void)" : "?CreateStandardColorTable@BMP@@QAE_NXZ",
    "?FlipWORD@@YAGG@Z" : "unsigned short FlipWORD(unsigned short)",
    "??0BMP@@QAE@XZ" : "BMP::BMP(void)",
    "?SetPixel@BMP@@QAE_NHHURGBApixel@@@Z" : "bool BMP::SetPixel(int,int RGBApixel)",
    "?Read32bitRow@BMP@@AAE_NPAEHH@Z" : "bool BMP::Read32bitRow(unsigned char *,int,int)",
    "?ReadFromFile@BMP@@QAE_NPBD@Z" : "bool BMP::ReadFromFile(char const *)",
    "?display@BMIH@@QAEXXZ" : "void BMIH::display(void)",
    "?Square@@YANN@Z" : "double Square(double)",
    "?FindClosestColor@BMP@@AAEEAAURGBApixel@@@Z" : "unsigned char BMP::FindClosestColor RGBApixel &)",
    "?Read24bitRow@BMP@@AAE_NPAEHH@Z" : "bool BMP::Read24bitRow(unsigned char *,int,int)",
    "?TellBitDepth@BMP@@QAEHXZ" : "int BMP::TellBitDepth(void)",
    "?Write24bitRow@BMP@@AAE_NPAEHH@Z" : "bool BMP::Write24bitRow(unsigned char *,int,int)",
    "??0BMIH@@QAE@XZ" : "BMIH::BMIH(void)",
    "?TellWidth@BMP@@QAEHXZ" : "int BMP::TellWidth(void)",
    "?Write1bitRow@BMP@@AAE_NPAEHH@Z" : "bool BMP::Write1bitRow(unsigned char *,int,int)",
    "??4RGBApixel@@QAEAAU0@ABU0@@Z" : "RGBApixel & RGBApixel::operator= RGBApixel const &)",
    "?TellVerticalDPI@BMP@@QAEHXZ" : "int BMP::TellVerticalDPI(void)",
    "?WriteToFile@BMP@@QAE_NPBD@Z" : "bool BMP::WriteToFile(char const *)",
    "?Read4bitRow@BMP@@AAE_NPAEHH@Z" : "bool BMP::Read4bitRow(unsigned char *,int,int)",
    "?SetDPI@BMP@@QAEXHH@Z" : "void BMP::SetDPI(int,int)",
    "?IntSquare@@YAHH@Z" : "int IntSquare(int)",
    "?Write32bitRow@BMP@@AAE_NPAEHH@Z" : "bool BMP::Write32bitRow(unsigned char *,int,int)",
    "??4BMFH@@QAEAAV0@ABV0@@Z" : "BMFH & BMFH::operator= BMFH const &)",
    "?Read1bitRow@BMP@@AAE_NPAEHH@Z" : "bool BMP::Read1bitRow(unsigned char *,int,int)",
    "??0BMFH@@QAE@XZ" : "BMFH::BMFH(void)",
    "??0BMP@@QAE@AAV0@@Z" : "BMP::BMP BMP &)",
    "?Write4bitRow@BMP@@AAE_NPAEHH@Z" : "bool BMP::Write4bitRow(unsigned char *,int,int)",
    "?FlipDWORD@@YAII@Z" : "unsigned int FlipDWORD(unsigned int)",
    "?TellHeight@BMP@@QAEHXZ" : "int BMP::TellHeight(void)",
    "?IsBigEndian@@YA_NXZ" : "bool IsBigEndian(void)",
    "?GetPixel@BMP@@QBE?AURGBApixel@@HH@Z" : "RGBApixel BMP::GetPixel(int,int)const",
    "?SetBitDepth@BMP@@QAE_NH@Z" : "bool BMP::SetBitDepth(int)",
    "?SwitchEndianess@BMIH@@QAEXXZ" : "void BMIH::SwitchEndianess(void)",
    "?TellNumberOfColors@BMP@@QAEHXZ" : "int BMP::TellNumberOfColors(void)",
    "??4BMP@@QAEAAV0@ABV0@@Z" : "BMP & BMP::operator= BMP const &)",
    "?SetColor@BMP@@QAE_NHURGBApixel@@@Z" : "bool BMP::SetColor(int RGBApixel)",
    "?SwitchEndianess@BMFH@@QAEXXZ" : "void BMFH::SwitchEndianess(void)",
    "?display@BMFH@@QAEXXZ" : "void BMFH::display(void)",
    "?SetSize@BMP@@QAE_NHH@Z" : "bool BMP::SetSize(int,int)",
    "?Read8bitRow@BMP@@AAE_NPAEHH@Z" : "bool BMP::Read8bitRow(unsigned char *,int,int)",
    "??4BMIH@@QAEAAV0@ABV0@@Z" : "BMIH & BMIH::operator= BMIH const &)",
    "?Write8bitRow@BMP@@AAE_NPAEHH@Z" : "bool BMP::Write8bitRow(unsigned char *,int,int)",
    "??1BMP@@QAE@XZ" : "BMP::~BMP(void)",
    "??RBMP@@QAEPAURGBApixel@@HH@Z" : "RGBApixel * BMP::operator()(int,int)",
    "?GetColor@BMP@@QAE?AURGBApixel@@H@Z" : "RGBApixel BMP::GetColor(int)",
    "?TellHorizontalDPI@BMP@@QAEHXZ" : "int BMP::TellHorizontalDPI(void)",
    "?CreateStandardColorTable@BMP@@QAE_NXZ" : "bool BMP::CreateStandardColorTable(void)",
}

class BMFH(ctypes.Structure):
    """class BMFH"""

    def __init__( self, *args ):
        """BMFH::BMFH(void)"""
        return self._methods_['__init__']( ctypes.pointer( self ), *args )

    def display( self, *args ):
        """void BMFH::display(void)"""
        return self._methods_['display']( ctypes.pointer( self ), *args )

    def SwitchEndianess( self, *args ):
        """void BMFH::SwitchEndianess(void)"""
        return self._methods_['SwitchEndianess']( ctypes.pointer( self ), *args )

class BMIH(ctypes.Structure):
    """class BMIH"""

    def __init__( self, *args ):
        """BMIH::BMIH(void)"""
        return self._methods_['__init__']( ctypes.pointer( self ), *args )

    def display( self, *args ):
        """void BMIH::display(void)"""
        return self._methods_['display']( ctypes.pointer( self ), *args )

    def SwitchEndianess( self, *args ):
        """void BMIH::SwitchEndianess(void)"""
        return self._methods_['SwitchEndianess']( ctypes.pointer( self ), *args )

class BMP(ctypes.Structure):
    """class BMP"""

    def TellBitDepth( self, *args ):
        """int BMP::TellBitDepth(void)"""
        return self._methods_['TellBitDepth']( ctypes.pointer( self ), *args )

    def TellWidth( self, *args ):
        """int BMP::TellWidth(void)"""
        return self._methods_['TellWidth']( ctypes.pointer( self ), *args )

    def TellHeight( self, *args ):
        """int BMP::TellHeight(void)"""
        return self._methods_['TellHeight']( ctypes.pointer( self ), *args )

    def TellNumberOfColors( self, *args ):
        """int BMP::TellNumberOfColors(void)"""
        return self._methods_['TellNumberOfColors']( ctypes.pointer( self ), *args )

    def SetDPI( self, *args ):
        """void BMP::SetDPI(int,int)"""
        return self._methods_['SetDPI']( ctypes.pointer( self ), *args )

    def TellVerticalDPI( self, *args ):
        """int BMP::TellVerticalDPI(void)"""
        return self._methods_['TellVerticalDPI']( ctypes.pointer( self ), *args )

    def TellHorizontalDPI( self, *args ):
        """int BMP::TellHorizontalDPI(void)"""
        return self._methods_['TellHorizontalDPI']( ctypes.pointer( self ), *args )

    def __init__( self, *args ):
        """BMP::BMP(void)"""
        return self._methods_['__init__']( ctypes.pointer( self ), *args )

    def __del__( self ):
        """BMP::~BMP(void)"""
        return self._methods_['__del__']( ctypes.pointer( self ) )

    def GetPixel( self, *args ):
        """RGBApixel BMP::GetPixel(int,int)const"""
        return self._methods_['GetPixel']( ctypes.pointer( self ), *args )

    def CreateStandardColorTable( self, *args ):
        """bool BMP::CreateStandardColorTable(void)"""
        return self._methods_['CreateStandardColorTable']( ctypes.pointer( self ), *args )

    def SetSize( self, *args ):
        """bool BMP::SetSize(int,int)"""
        return self._methods_['SetSize']( ctypes.pointer( self ), *args )

    def SetBitDepth( self, *args ):
        """bool BMP::SetBitDepth(int)"""
        return self._methods_['SetBitDepth']( ctypes.pointer( self ), *args )

    def WriteToFile( self, *args ):
        """bool BMP::WriteToFile(char const *)"""
        return self._methods_['WriteToFile']( ctypes.pointer( self ), *args )

    def ReadFromFile( self, *args ):
        """bool BMP::ReadFromFile(char const *)"""
        return self._methods_['ReadFromFile']( ctypes.pointer( self ), *args )

    def GetColor( self, *args ):
        """RGBApixel BMP::GetColor(int)"""
        return self._methods_['GetColor']( ctypes.pointer( self ), *args )

    def Read32bitRow( self, *args ):
        """bool BMP::Read32bitRow(unsigned char *,int,int)"""
        return self._methods_['Read32bitRow']( ctypes.pointer( self ), *args )

    def Read24bitRow( self, *args ):
        """bool BMP::Read24bitRow(unsigned char *,int,int)"""
        return self._methods_['Read24bitRow']( ctypes.pointer( self ), *args )

    def Read8bitRow( self, *args ):
        """bool BMP::Read8bitRow(unsigned char *,int,int)"""
        return self._methods_['Read8bitRow']( ctypes.pointer( self ), *args )

    def Read4bitRow( self, *args ):
        """bool BMP::Read4bitRow(unsigned char *,int,int)"""
        return self._methods_['Read4bitRow']( ctypes.pointer( self ), *args )

    def Read1bitRow( self, *args ):
        """bool BMP::Read1bitRow(unsigned char *,int,int)"""
        return self._methods_['Read1bitRow']( ctypes.pointer( self ), *args )

    def Write32bitRow( self, *args ):
        """bool BMP::Write32bitRow(unsigned char *,int,int)"""
        return self._methods_['Write32bitRow']( ctypes.pointer( self ), *args )

    def Write24bitRow( self, *args ):
        """bool BMP::Write24bitRow(unsigned char *,int,int)"""
        return self._methods_['Write24bitRow']( ctypes.pointer( self ), *args )

    def Write8bitRow( self, *args ):
        """bool BMP::Write8bitRow(unsigned char *,int,int)"""
        return self._methods_['Write8bitRow']( ctypes.pointer( self ), *args )

    def Write4bitRow( self, *args ):
        """bool BMP::Write4bitRow(unsigned char *,int,int)"""
        return self._methods_['Write4bitRow']( ctypes.pointer( self ), *args )

    def Write1bitRow( self, *args ):
        """bool BMP::Write1bitRow(unsigned char *,int,int)"""
        return self._methods_['Write1bitRow']( ctypes.pointer( self ), *args )

class RGBApixel(ctypes.Structure):
    """class RGBApixel"""

BMFH._fields_ = [ #class BMFH
    ("bfType", ctypes.c_ushort),
    ("bfSize", ctypes.c_uint),
    ("bfReserved1", ctypes.c_ushort),
    ("bfReserved2", ctypes.c_ushort),
    ("bfOffBits", ctypes.c_uint),
]

mfcreator = ctypes_utils.mem_fun_factory( easybmplib, BMFH, "BMFH" )
BMFH._methods_ = { #class non-virtual member functions definition list
    "__init__" : mfcreator.default_constructor(),

    "display" : mfcreator( "void BMFH::display(void)" ),

    "SwitchEndianess" : mfcreator( "void BMFH::SwitchEndianess(void)" ),
}
del mfcreator

BMIH._fields_ = [ #class BMIH
    ("biSize", ctypes.c_uint),
    ("biWidth", ctypes.c_uint),
    ("biHeight", ctypes.c_uint),
    ("biPlanes", ctypes.c_ushort),
    ("biBitCount", ctypes.c_ushort),
    ("biCompression", ctypes.c_uint),
    ("biSizeImage", ctypes.c_uint),
    ("biXPelsPerMeter", ctypes.c_uint),
    ("biYPelsPerMeter", ctypes.c_uint),
    ("biClrUsed", ctypes.c_uint),
    ("biClrImportant", ctypes.c_uint),
]

mfcreator = ctypes_utils.mem_fun_factory( easybmplib, BMIH, "BMIH" )
BMIH._methods_ = { #class non-virtual member functions definition list
    "__init__" : mfcreator.default_constructor(),

    "display" : mfcreator( "void BMIH::display(void)" ),

    "SwitchEndianess" : mfcreator( "void BMIH::SwitchEndianess(void)" ),
}
del mfcreator

RGBApixel._fields_ = [ #class RGBApixel
    ("Blue", ctypes.c_ubyte),
    ("Green", ctypes.c_ubyte),
    ("Red", ctypes.c_ubyte),
    ("Alpha", ctypes.c_ubyte),
]

mfcreator = ctypes_utils.mem_fun_factory( easybmplib, RGBApixel, "RGBApixel" )
RGBApixel._methods_ = { #class non-virtual member functions definition list

}
del mfcreator

BMP._fields_ = [ #class BMP
    ("BitDepth", ctypes.c_int),
    ("Width", ctypes.c_int),
    ("Height", ctypes.c_int),
    ("Pixels", ctypes.POINTER( ctypes.POINTER( RGBApixel ) )),
    ("Colors", ctypes.POINTER( RGBApixel )),
    ("XPelsPerMeter", ctypes.c_int),
    ("YPelsPerMeter", ctypes.c_int),
    ("MetaData1", ctypes.POINTER( ctypes.c_ubyte )),
    ("SizeOfMetaData1", ctypes.c_int),
    ("MetaData2", ctypes.POINTER( ctypes.c_ubyte )),
    ("SizeOfMetaData2", ctypes.c_int),
]

mfcreator = ctypes_utils.mem_fun_factory( easybmplib, BMP, "BMP" )
BMP._methods_ = { #class non-virtual member functions definition list
    "TellBitDepth" : mfcreator( "int BMP::TellBitDepth(void)", restype=ctypes.c_int ),

    "TellWidth" : mfcreator( "int BMP::TellWidth(void)", restype=ctypes.c_int ),

    "TellHeight" : mfcreator( "int BMP::TellHeight(void)", restype=ctypes.c_int ),

    "TellNumberOfColors" : mfcreator( "int BMP::TellNumberOfColors(void)", restype=ctypes.c_int ),

    "SetDPI" : mfcreator( "void BMP::SetDPI(int,int)", argtypes=[ ctypes.c_int, ctypes.c_int ] ),

    "TellVerticalDPI" : mfcreator( "int BMP::TellVerticalDPI(void)", restype=ctypes.c_int ),

    "TellHorizontalDPI" : mfcreator( "int BMP::TellHorizontalDPI(void)", restype=ctypes.c_int ),

    "__init__" : mfcreator.default_constructor(),

    "__del__" : mfcreator.destructor(is_virtual=False),

    "GetPixel" : mfcreator( "RGBApixel BMP::GetPixel(int,int)const", restype=RGBApixel, argtypes=[ ctypes.c_int, ctypes.c_int ] ),

    "CreateStandardColorTable" : mfcreator( "bool BMP::CreateStandardColorTable(void)", restype=ctypes.c_bool ),

    "SetSize" : mfcreator( "bool BMP::SetSize(int,int)", restype=ctypes.c_bool, argtypes=[ ctypes.c_int, ctypes.c_int ] ),

    "SetBitDepth" : mfcreator( "bool BMP::SetBitDepth(int)", restype=ctypes.c_bool, argtypes=[ ctypes.c_int ] ),

    "WriteToFile" : mfcreator( "bool BMP::WriteToFile(char const *)", restype=ctypes.c_bool, argtypes=[ ctypes.c_char_p ] ),

    "ReadFromFile" : mfcreator( "bool BMP::ReadFromFile(char const *)", restype=ctypes.c_bool, argtypes=[ ctypes.c_char_p ] ),

    "GetColor" : mfcreator( "RGBApixel BMP::GetColor(int)", restype=RGBApixel, argtypes=[ ctypes.c_int ] ),

    "Read32bitRow" : mfcreator( "bool BMP::Read32bitRow(unsigned char *,int,int)", restype=ctypes.c_bool, argtypes=[ ctypes.POINTER( ctypes.c_ubyte ), ctypes.c_int, ctypes.c_int ] ),

    "Read24bitRow" : mfcreator( "bool BMP::Read24bitRow(unsigned char *,int,int)", restype=ctypes.c_bool, argtypes=[ ctypes.POINTER( ctypes.c_ubyte ), ctypes.c_int, ctypes.c_int ] ),

    "Read8bitRow" : mfcreator( "bool BMP::Read8bitRow(unsigned char *,int,int)", restype=ctypes.c_bool, argtypes=[ ctypes.POINTER( ctypes.c_ubyte ), ctypes.c_int, ctypes.c_int ] ),

    "Read4bitRow" : mfcreator( "bool BMP::Read4bitRow(unsigned char *,int,int)", restype=ctypes.c_bool, argtypes=[ ctypes.POINTER( ctypes.c_ubyte ), ctypes.c_int, ctypes.c_int ] ),

    "Read1bitRow" : mfcreator( "bool BMP::Read1bitRow(unsigned char *,int,int)", restype=ctypes.c_bool, argtypes=[ ctypes.POINTER( ctypes.c_ubyte ), ctypes.c_int, ctypes.c_int ] ),

    "Write32bitRow" : mfcreator( "bool BMP::Write32bitRow(unsigned char *,int,int)", restype=ctypes.c_bool, argtypes=[ ctypes.POINTER( ctypes.c_ubyte ), ctypes.c_int, ctypes.c_int ] ),

    "Write24bitRow" : mfcreator( "bool BMP::Write24bitRow(unsigned char *,int,int)", restype=ctypes.c_bool, argtypes=[ ctypes.POINTER( ctypes.c_ubyte ), ctypes.c_int, ctypes.c_int ] ),

    "Write8bitRow" : mfcreator( "bool BMP::Write8bitRow(unsigned char *,int,int)", restype=ctypes.c_bool, argtypes=[ ctypes.POINTER( ctypes.c_ubyte ), ctypes.c_int, ctypes.c_int ] ),

    "Write4bitRow" : mfcreator( "bool BMP::Write4bitRow(unsigned char *,int,int)", restype=ctypes.c_bool, argtypes=[ ctypes.POINTER( ctypes.c_ubyte ), ctypes.c_int, ctypes.c_int ] ),

    "Write1bitRow" : mfcreator( "bool BMP::Write1bitRow(unsigned char *,int,int)", restype=ctypes.c_bool, argtypes=[ ctypes.POINTER( ctypes.c_ubyte ), ctypes.c_int, ctypes.c_int ] ),
}
del mfcreator

Square_type = ctypes.CFUNCTYPE( ctypes.c_double, ctypes.c_double  )
Square = Square_type( ( easybmplib.undecorated_names["double Square(double)"], easybmplib ) )

IntSquare_type = ctypes.CFUNCTYPE( ctypes.c_int, ctypes.c_int  )
IntSquare = IntSquare_type( ( easybmplib.undecorated_names["int IntSquare(int)"], easybmplib ) )

FlipDWORD_type = ctypes.CFUNCTYPE( ctypes.c_uint, ctypes.c_uint  )
FlipDWORD = FlipDWORD_type( ( easybmplib.undecorated_names["unsigned int FlipDWORD(unsigned int)"], easybmplib ) )

IsBigEndian_type = ctypes.CFUNCTYPE( ctypes.c_bool )
IsBigEndian = IsBigEndian_type( ( easybmplib.undecorated_names["bool IsBigEndian(void)"], easybmplib ) )

FlipWORD_type = ctypes.CFUNCTYPE( ctypes.c_ushort, ctypes.c_ushort  )
FlipWORD = FlipWORD_type( ( easybmplib.undecorated_names["unsigned short FlipWORD(unsigned short)"], easybmplib ) )
