/*********************************************************************/
/*    monotype-testprogram : testing pointer-routines                */
/*                                                                   */
/*                                                                   */
/*********************************************************************/

#include <stdio.h>
#include <conio.h>
#include <dos.h>
#include <fcntl.h>          /* O_ constant definitions */
#include <graph.h>
#include <io.h>
#include <process.h>
#include <ctype.h>
#include <stdlib.h>
#include <sys\types.h>
#include <sys\stat.h>
#include <string.h>
#include <graph.h>


/* Macro to define cursor lines */

#define CURSOR(start,end) (((start) << 8) | (end))

#define AAN             1
#define UIT             0
#define INVOEGEN      772
#define OVERSCHRIJVEN   7
#define UNDERLINE       0x0707
#define FULLBLOCK       0x0007
#define DOUBLEUNDERLINE 0x0607
#define NOCURSOR        0x2000

/*
       0x0707          Underline
       0x0007          Full block cursor
       0x0607          Double underline
       0x2000          No cursor
 */

#define MAXOPSLAG    1500
#define ROMEIN          0
#define CURSIEF         1
#define KLEINKAP        2
#define VET             3

#define MAXRIJ         14   /* 15 rijen systeem */
#define NORMAAL         1   /* diverse code systemen Monotype */
#define MNH             2
#define SHIFT           3

/*            ONML KJIH GFsE DgCB A123 4567 89ab cdek    */
/*                                                      */

const unsigned long kcodes[17] =
	{ 0x44000000, /* NI 0*/
	  0x50000000, /* NL 1*/
	      0x8000, /* A  2*/
	     0x10000, /* B  3*/
	     0x20000, /* C  4*/
	     0x80000, /* D  5*/
	    0x100000, /* E  6*/
	    0x400000, /* F  7*/
	    0x800000, /* G  8*/
	   0x1000000, /* H  9*/
	   0x2000000, /* I  a*/
	   0x4000000, /* J  b*/
	   0x8000000, /* K  c*/
	  0x10000000, /* L  d*/
	  0x20000000, /* M  e*/
	  0x40000000, /* N  f*/
	  0x80000000  /* O   */
	   };

const unsigned long rcodes[16] =
	 /*  1     2       3      4       5       6     7 */
	{ 0x4000, 0x2000, 0x1000, 0x800, 0x400, 0x200, 0x100,
	 /* 8     9    a     b     c    d    e    f   */
	  0x80, 0x40, 0x20, 0x10, 0x8, 0x4, 0x2, 0x80000000, 0x0 };

const unsigned long _NJKgk  = 0x4c040001;
const unsigned long _NKg    = 0x48000000;
const unsigned long _NJgk   = 0x44040001;
const unsigned long _Snaald =   0x200000;
const unsigned long _G1     =   0x804000;
const unsigned long _G2     =   0x802000;
const unsigned long _GS1    =   0xa04000;
const unsigned long _GS2    =   0xa02000;
const unsigned long _G5     =   0x800400;
const unsigned long _015    = 0x80000000;

/* RECORDS1.C illustrates reading and writing of file records using seek
 * functions including:
 *      fseek       rewind      ftell
 *
 * Other general functions illustrated include:
 *      tmpfile     rmtmp       fread       fwrite
 *
 * Also illustrated:
 *      struct
 *
 * See RECORDS2.C for a version of this program using fgetpos and fsetpos.
 */

/* structure definitions */

/* File record */

struct RECORD
{
    int     integer;
    long    doubleword;
    double  realnum;
    char    string[15];
} filerec = { 0, 1, 10000000.0, "eel sees tar" };

struct data_matrix {
     char charname[40];         /* naam letter */
     char nummers[25];          /* monotype aanduidingen */
     unsigned int  set;         /* width largest character in pica-points * 4 */
     unsigned int  corps[2];    /* corps engels / didot in 1/2 punten */
     char charwedge[8];         /* monotype aanduiding wig  */
     unsigned int cwedge[16];   /* indeling wig */
	    /* a:\\mat00001.mat"
	       12 3456789012345 678901234
	    */
     char filenaam[30];         /* filenaam van matrix-file */
     unsigned int aantal; /* aantal letters in file */
} centerrec = {
     "",
     "",
     0,0, 0,
     "",
     5,6,7,8,9, 9,9,10,10,11, 13,14,16,17,18, 18,
     "a:\\mat00000.mon",
     0
} ;

struct data_matrix garamond = {
      "Garamond 12 punt didot",
      "156 i:156,174 b:201",
      45, 26, 24,
      "156",
      5,6,7,8,9, 9,9,10,10,11, 13,14,15,17,18, 18,
      "a:\\mat00001.mon",
      263
} ;

typedef struct mmtype {
     char _ligature[4];        /* room for 3 chars: ffi, ffl max...   */
     unsigned char _kind;      /* roman, italic, small cap, bold      */
     unsigned char _width;     /* nominal witdh in units              */
     unsigned char _row;       /* row in matrix                       */
     unsigned char _col;       /* colom in matrix                     */
			       /* 0-16, 17=> outside matrix !         */
     unsigned long int _code;  /* the actual code                     */
     unsigned char _u[2];      /* uitvulling / wedges-positions       */
};

struct m_type {

     unsigned int naam;       /* voor testen routines                */
     char ligature[3];        /* room for 3 chars: ffi, ffl max...   */
     unsigned char kind;      /* roman, italic, small cap, bold      */
     unsigned char width;     /* nominal witdh in units              */
     char row;                /* row in matrix                       */
     char col;                /* colom in matrix                     */
			      /* 0-16, 17=> outside matrix !         */
     unsigned long int code;  /* the actual code                     */
     unsigned char u[2];      /* uitvulling / wedges-positions       */

     struct m_type * _fore;   /* verwijzen            */
     struct m_type * _next;   /* verwijzen in de ring */
}
     garamnd12[275] /* [255] */ = {

     0,  "j",1, 5, 0, 0, 0x44004000,3,8, NULL,&garamnd12[1],
     1,  "l",1, 5, 0, 1, 0x50004000,3,8, &garamnd12[0], &garamnd12[2],
     2,  "i",1, 9, 0, 2,     0xc000,3,8, &garamnd12[1], &garamnd12[3],
     3,  ".",0, 5, 0, 3,    0x14000,3,8, &garamnd12[2], &garamnd12[5],
     4,  ",",0, 5, 0, 4,    0x24000,3,8, &garamnd12[3], &garamnd12[5],
     5, "\'",0, 5, 0, 5,    0x84000,3,8, &garamnd12[3], &garamnd12[6],
     6,  "j",0, 5, 0, 6,   0x104000,3,8, &garamnd12[5], &garamnd12[7],
     7,  "i",0, 5, 0, 7,   0x404000,3,8, &garamnd12[6], &garamnd12[8],
     8,  " ",0, 5, 0, 8,   0x804000,3,8, &garamnd12[7], &garamnd12[9],
     9,  "l",0, 5, 0, 9,  0x1004000,3,8, &garamnd12[8],&garamnd12[10],
    10,  "(",0, 5, 0,10,  0x2004000,3,8, &garamnd12[9],&garamnd12[11],
   11,"\214",0, 5, 0,11,  0x4004000,3,8,&garamnd12[10],&garamnd12[12],
    12,  ":",0, 5, 0,12,  0x8004000,3,8,&garamnd12[11],&garamnd12[13],
    13,  ":",1, 5, 0,13, 0x10004000,3,8,&garamnd12[12],&garamnd12[14],
   14,"\213",0, 5, 0,14, 0x20004000,3,8,&garamnd12[13],&garamnd12[15],
    15,  "`",0, 5, 0,15, 0x40004000,3,8,&garamnd12[14],&garamnd12[16],
    16,  "#",2, 5, 0,16, 0x80004000,3,8,&garamnd12[15],&garamnd12[272],
	 /* hoogspatie*/

    17,  "i",2, 6, 1, 0, 0x44002000,3,8,&garamnd12[274],&garamnd12[18],
   18,"\211",1, 6, 1, 1, 0x50002000,3,8,&garamnd12[17],&garamnd12[19],
    19,  "c",1, 6, 1, 2,     0xa000,3,8,&garamnd12[18],&garamnd12[20],
    20,  "s",1, 6, 1, 3,    0x12000,3,8,&garamnd12[19],&garamnd12[21],
    21,  "f",1, 6, 1, 4,    0x22000,3,8,&garamnd12[20],&garamnd12[22],
    22,  "t",1, 6, 1, 5,    0x82000,3,8,&garamnd12[21],&garamnd12[23],
    23,  "e",1, 6, 1, 6,   0x102000,3,8,&garamnd12[22],&garamnd12[24],
    24,  "f",0, 6, 1, 7,   0x402000,3,8,&garamnd12[23],&garamnd12[25],
    25,  " ",1, 6, 1, 8,   0x802000,3,8,&garamnd12[24],&garamnd12[26],
    26,  "t",0, 6, 1, 9,  0x1002000,3,8,&garamnd12[25],&garamnd12[27],
    27,  "-",0, 6, 1,10,  0x2002000,3,8,&garamnd12[26],&garamnd12[28],
    28,  ")",0, 6, 1,11,  0x4002000,3,8,&garamnd12[27],&garamnd12[29],
    29,  "i",3, 6, 1,12,  0x8002000,3,8,&garamnd12[28],&garamnd12[30],
    30,  ";",1, 5, 1,13, 0x10002000,3,8,&garamnd12[29],&garamnd12[31],
    31,  "t",3, 6, 1,14, 0x20002000,3,8,&garamnd12[30],&garamnd12[32],
    32,  "[",0, 6, 1,15, 0x40002000,3,8,&garamnd12[31],&garamnd12[33],
    33,  "]",0, 6, 1,16, 0x80002000,3,8,&garamnd12[32],&garamnd12[255],

    34,  "j",2, 7, 2, 0, 0x44001000,3,8,&garamnd12[257],&garamnd12[35],
    35,  "s",2, 7, 2, 1, 0x50001000,3,8,&garamnd12[34],&garamnd12[36],
   36,"\224",1, 7, 2, 2,     0x9000,3,8,&garamnd12[35],&garamnd12[37],
    37,  "v",1, 7, 2, 3,    0x11000,3,8,&garamnd12[36],&garamnd12[38],
    38,  "y",1, 7, 2, 4,    0x21000,3,8,&garamnd12[37],&garamnd12[39],
    39,  "g",1, 7, 2, 5,    0x81000,3,8,&garamnd12[38],&garamnd12[40],
    40,  "r",1, 7, 2, 6,   0x101000,3,8,&garamnd12[39],&garamnd12[41],
    41,  "o",1, 7, 2, 7,   0x401000,3,8,&garamnd12[40],&garamnd12[42],
    42,  "r",0, 7, 2, 8,   0x801000,3,8,&garamnd12[41],&garamnd12[43],
    43,  "s",0, 7, 2, 9,  0x1001000,3,8,&garamnd12[42],&garamnd12[44],
    44,  "i",3, 7, 2,10,  0x2001000,3,8,&garamnd12[43],&garamnd12[45],
    45,  ":",3, 7, 2,11,  0x4001000,3,8,&garamnd12[44],&garamnd12[46],
    46,  ";",3, 7, 2,12,  0x8001000,3,8,&garamnd12[45],&garamnd12[47],
    47, "\!",0, 7, 2,13, 0x10001000,3,8,&garamnd12[46],&garamnd12[48],
    48,  "r",3, 7, 2,14, 0x20001000,3,8,&garamnd12[47],&garamnd12[49],
    49,  "I",3, 7, 2,15, 0x40001000,3,8,&garamnd12[48],&garamnd12[50],
    50,  "-",3, 7, 2,16, 0x80001000,3,8,&garamnd12[49],&garamnd12[51],

    51,  "p",2, 8, 3, 0, 0x44000800,3,8,&garamnd12[50],&garamnd12[52],
    52,  "J",1, 8, 3, 1, 0x50000800,3,8,&garamnd12[51],&garamnd12[53],
    53,  "I",1, 8, 3, 2,     0x8800,3,8,&garamnd12[52],&garamnd12[54],
    54,  "q",1, 8, 3, 3,    0x10800,3,8,&garamnd12[53],&garamnd12[55],
    55,  "b",1, 8, 3, 4,    0x20800,3,8,&garamnd12[54],&garamnd12[56],
    56,  "d",1, 8, 3, 5,    0x80800,3,8,&garamnd12[55],&garamnd12[57],
    57,  "h",1, 8, 3, 6,   0x100800,3,8,&garamnd12[56],&garamnd12[58],
    58,  "n",1, 8, 3, 7,   0x400800,3,8,&garamnd12[57],&garamnd12[59],
    59,  "a",0, 8, 3, 8,   0x800800,3,8,&garamnd12[58],&garamnd12[60],
    60,  "u",0, 8, 3, 9,  0x1000800,3,8,&garamnd12[59],&garamnd12[61],
    61,  "a",3, 8, 3,10,  0x2000800,3,8,&garamnd12[60],&garamnd12[62],
    62,  "e",3, 8, 3,11,  0x4000800,3,8,&garamnd12[61],&garamnd12[63],
    63,  "c",3, 8, 3,12,  0x8000800,3,8,&garamnd12[62],&garamnd12[64],
    64,  "z",0, 8, 3,13, 0x10000800,3,8,&garamnd12[63],&garamnd12[65],
   65,"\204",3, 8, 3,14, 0x20000800,3,8,&garamnd12[64],&garamnd12[66],
   66,"\205",3, 8, 3,15, 0x40000800,3,8,&garamnd12[65],&garamnd12[67],
   67,"\240",3, 8, 3,16, 0x80000800,3,8,&garamnd12[66],&garamnd12[258],


    68,  "y",2, 9, 4, 0, 0x44000400,3,8,&garamnd12[266],&garamnd12[69],
    69,  "b",2, 9, 4, 1, 0x50000400,3,8,&garamnd12[68],&garamnd12[70],
    70,  "l",2, 9, 4, 2,     0x8400,3,8,&garamnd12[69],&garamnd12[71],
    71,  "e",2, 9, 4, 3,    0x10400,3,8,&garamnd12[70],&garamnd12[72],
    72, "\?",1, 9, 4, 4,    0x20400,3,8,&garamnd12[71],&garamnd12[73],
    73, "\!",1, 9, 4, 5,    0x80400,3,8,&garamnd12[72],&garamnd12[74],
   74,"\152",1, 9, 4, 6,   0x100400,3,8,&garamnd12[73],&garamnd12[75],
    75,  "p",1, 9, 4, 7,   0x400400,3,8,&garamnd12[74],&garamnd12[76],
    76,  " ",2, 9, 4, 8,   0x800400,3,8,&garamnd12[75],&garamnd12[77],
    77, "fi",0, 9, 4, 9,  0x1000400,3,8,&garamnd12[76],&garamnd12[78],
    78,  "3",0, 9, 4,10,  0x2000400,3,8,&garamnd12[77],&garamnd12[79],
    79,  "6",0, 9, 4,11,  0x4000400,3,8,&garamnd12[78],&garamnd12[80],
    80,  "9",0, 9, 4,12,  0x8000400,3,8,&garamnd12[79],&garamnd12[81],
    81,  "5",0, 9, 4,13, 0x10000400,3,8,&garamnd12[80],&garamnd12[82],
    82,  "8",3, 9, 4,14, 0x20000400,3,8,&garamnd12[81],&garamnd12[83],
    83,  "a",3, 9, 4,15, 0x40000400,3,8,&garamnd12[82],&garamnd12[84],
    84,  "z",3, 9, 4,16, 0x80000400,3,8,&garamnd12[83],&garamnd12[85],

    85,  "z",2, 9, 5, 0, 0x44000200,3,8,&garamnd12[84],&garamnd12[86],
    86,  "f",2, 9, 5, 1, 0x50000200,3,8,&garamnd12[85],&garamnd12[87],
    87,  "t",2, 9, 5, 2,     0x8200,3,8,&garamnd12[86],&garamnd12[88],
    88,  "(",1, 9, 5, 3,    0x10200,3,8,&garamnd12[87],&garamnd12[89],
    89, "fi",1, 9, 5, 4,    0x20200,3,8,&garamnd12[88],&garamnd12[90],
    90, "fl",1, 9, 5, 5,    0x80200,3,8,&garamnd12[89],&garamnd12[91],
    91,  "z",1, 9, 5, 6,   0x100200,3,8,&garamnd12[90],&garamnd12[92],
    92, "\?",1, 9, 5, 7,   0x400200,3,8,&garamnd12[91],&garamnd12[93],
    93,  "x",0, 9, 5, 8,   0x800200,3,8,&garamnd12[92],&garamnd12[94],
    94,  "y",0, 9, 5, 9,  0x1000200,3,8,&garamnd12[93],&garamnd12[95],
    95,  "7",0, 9, 5,10,  0x2000200,3,8,&garamnd12[94],&garamnd12[96],
    96,  "4",0, 9, 5,11,  0x4000200,3,8,&garamnd12[95],&garamnd12[97],
    97,  "1",0, 9, 5,12,  0x8000200,3,8,&garamnd12[96],&garamnd12[98],
    98,  "0",0, 9, 5,13, 0x10000200,3,8,&garamnd12[97],&garamnd12[99],
    99,  "2",0, 9, 5,14, 0x20000200,3,8,&garamnd12[98],&garamnd12[100],
   100,  "1",3, 9, 5,15, 0x40000200,3,8,&garamnd12[99],&garamnd12[101],
   101,  "c",3, 9, 5,16, 0x80000200,3,8,&garamnd12[100],&garamnd12[267],

   102,  "x",2,10, 6, 0, 0x44000100,3,8,&garamnd12[269],&garamnd12[103],
   103,  "S",1,10, 6, 1, 0x50000100,3,8,&garamnd12[102],&garamnd12[104],
   104,  "u",2,10, 6, 2,     0x8100,3,8,&garamnd12[103],&garamnd12[105],
   105,  "o",2,10, 6, 3,    0x10100,3,8,&garamnd12[104],&garamnd12[106],
   106, "fj",0,10, 6, 4,    0x20100,3,8,&garamnd12[105],&garamnd12[107],
   107,  "k",1,10, 6, 5,    0x80100,3,8,&garamnd12[106],&garamnd12[108],
   108,  "q",0,10, 6, 6,   0x100100,3,8,&garamnd12[107],&garamnd12[109],
   109,  "h",0,10, 6, 7,   0x400100,3,8,&garamnd12[108],&garamnd12[110],
   110,  "p",0,10, 6, 8,   0x800100,3,8,&garamnd12[109],&garamnd12[111],
   111,  "g",0,10, 6, 9,  0x1000100,3,8,&garamnd12[110],&garamnd12[112],
  112,"\230",0,10, 6,10,  0x2000100,3,8,&garamnd12[111],&garamnd12[113],
   113,  "b",0,10, 6,11,  0x4000100,3,8,&garamnd12[112],&garamnd12[114],
   114, "ff",0,10, 6,12,  0x8000100,3,8,&garamnd12[113],&garamnd12[115],
   115, "fl",0,10, 6,13, 0x10000100,3,8,&garamnd12[114],&garamnd12[116],
   116, "fi",0,10, 6,14, 0x20000100,3,8,&garamnd12[115],&garamnd12[117],
   117,  "y",3,10, 6,15, 0x40000100,3,8,&garamnd12[116],&garamnd12[118],
   118,  "S",3,10, 6,16, 0x80000100,3,8,&garamnd12[117],&garamnd12[119],

   119,  "v",2,10, 7, 0, 0x44000080,3,8,&garamnd12[118],&garamnd12[120],
   120,  "c",2,10, 7, 1, 0x50000080,3,8,&garamnd12[119],&garamnd12[121],
   121,  "r",2,10, 7, 2,     0x8080,3,8,&garamnd12[120],&garamnd12[122],
   122,  "a",2,10, 7, 3,    0x10080,3,8,&garamnd12[121],&garamnd12[123],
   123, "ff",1,10, 7, 4,    0x20080,3,8,&garamnd12[122],&garamnd12[124],
   124,  "S",0,10, 7, 5,    0x80080,3,8,&garamnd12[123],&garamnd12[125],
   125,  "v",0,10, 7, 6,   0x100080,3,8,&garamnd12[124],&garamnd12[126],
   126,  "k",0,10, 7, 7,   0x400080,3,8,&garamnd12[125],&garamnd12[127],
   127,  "u",0,10, 7, 8,   0x800080,3,8,&garamnd12[126],&garamnd12[128],
   128,  "n",0,10, 7, 9,  0x1000080,3,8,&garamnd12[127],&garamnd12[129],
   129,  "o",0,10, 7,10,  0x2000080,3,8,&garamnd12[128],&garamnd12[130],
   130,  "d",0,10, 7,11,  0x4000080,3,8,&garamnd12[129],&garamnd12[131],
  131,"\224",0,10, 7,12,  0x8000080,3,8,&garamnd12[130],&garamnd12[132],
  132,"\201",0,10, 7,13, 0x10000080,3,8,&garamnd12[131],&garamnd12[133],
  133,"\341",0,10, 7,14, 0x20000080,3,8,&garamnd12[132],&garamnd12[134],
  134,"\225",0,10, 7,15, 0x40000080,3,8,&garamnd12[133],&garamnd12[135],
  135,"\242",0,10, 7,16, 0x80000080,3,8,&garamnd12[134],&garamnd12[270],

   136,  "k",2,11, 8, 0, 0x44000040,3,8,&garamnd12[271],&garamnd12[137],
   137,  "d",2,11, 8, 1, 0x50000040,3,8,&garamnd12[136],&garamnd12[138],
   138,  "g",2,11, 8, 2,     0x8040,3,8,&garamnd12[137],&garamnd12[139],
   139,  "n",2,11, 8, 3,    0x10040,3,8,&garamnd12[138],&garamnd12[140],
   140,  "w",1,11, 8, 4,    0x20040,3,8,&garamnd12[139],&garamnd12[141],
   141,  "x",1,11, 8, 5,    0x80040,3,8,&garamnd12[140],&garamnd12[142],
   142,  "F",1,11, 8, 6,   0x100040,3,8,&garamnd12[141],&garamnd12[143],
   143,  "P",0,11, 8, 7,   0x400040,3,8,&garamnd12[142],&garamnd12[144],
   144,  "u",0,11, 8, 8,   0x800040,3,8,&garamnd12[143],&garamnd12[145],
   145,  "n",3,11, 8, 9,  0x1000040,3,8,&garamnd12[144],&garamnd12[146],
  146,"\230",3,11, 8,10,  0x2000040,3,8,&garamnd12[145],&garamnd12[147],
   147,  "g",3,11, 8,11,  0x4000040,3,8,&garamnd12[146],&garamnd12[148],
   148,  "b",3,11, 8,12,  0x8000040,3,8,&garamnd12[147],&garamnd12[149],
   149,  "d",3,11, 8,13, 0x10000040,3,8,&garamnd12[148],&garamnd12[150],
   150,  "h",3,11, 8,14, 0x20000040,3,8,&garamnd12[149],&garamnd12[151],
   151,  "k",3,11, 8,15, 0x40000040,3,8,&garamnd12[150],&garamnd12[152],
   152,  "p",3,11, 8,16, 0x80000040,3,8,&garamnd12[151],&garamnd12[153],

   153,  "Q",1,12, 9, 0, 0x44000020,3,8,&garamnd12[152],&garamnd12[154],
   154,  "Y",1,12, 9, 1, 0x50000020,3,8,&garamnd12[153],&garamnd12[155],
   155,  "K",1,12, 9, 2,     0x8020,3,8,&garamnd12[154],&garamnd12[156],
   156,  "h",2,12, 9, 3,    0x10020,3,8,&garamnd12[155],&garamnd12[157],
   157,  "m",2,12, 9, 4,    0x20020,3,8,&garamnd12[156],&garamnd12[158],
   158,  "C",1,12, 9, 5,    0x80020,3,8,&garamnd12[157],&garamnd12[159],
   159,  "L",1,12, 9, 6,   0x100020,3,8,&garamnd12[158],&garamnd12[160],
   160,  "B",0,12, 9, 7,   0x400020,3,8,&garamnd12[159],&garamnd12[161],
   161,  "C",0,12, 9, 8,   0x800020,3,8,&garamnd12[160],&garamnd12[162],
   162,  "L",0,12, 9, 9,  0x1000020,3,8,&garamnd12[161],&garamnd12[163],
   163,  "F",3,12, 9,10,  0x2000020,3,8,&garamnd12[162],&garamnd12[165],
   164,   "",0,12, 9,11,  0x4000020,3,8,NULL,NULL,  /* 164 */
   165,  "O",1,12, 9,12,  0x8000020,3,8,&garamnd12[164],&garamnd12[167],
   166,   "",0,12, 9,13, 0x10000020,3,8,NULL,NULL,  /* 166 */
  167,"\200",0,12, 9,14, 0x20000020,3,8,&garamnd12[165],&garamnd12[170],
   168,   "",0,12, 9,15, 0x40000020,3,8,NULL,NULL,  /* 168 */
   169,   "",0,12, 9,16, 0x80000020,3,8,NULL,NULL,  /* 169 */

   170,"ffi",1,13,10, 0, 0x44000010,3,8,&garamnd12[167],&garamnd12[171],
   171,"ffl",1,13,10, 1, 0x50000010,3,8,&garamnd12[170],&garamnd12[172],
   172,  "G",1,13,10, 2,     0x8010,3,8,&garamnd12[171],&garamnd12[173],
   173,  "T",1,13,10, 3,    0x10010,3,8,&garamnd12[172],&garamnd12[174],
   174,  "Z",1,13,10, 4,    0x20010,3,8,&garamnd12[173],&garamnd12[175],
   175,  "B",1,13,10, 5,    0x80010,3,8,&garamnd12[174],&garamnd12[176],
   176,  "P",1,13,10, 6,   0x100010,3,8,&garamnd12[175],&garamnd12[177],
   177,  "U",1,13,10, 7,   0x400010,3,8,&garamnd12[176],&garamnd12[178],
   178,  "m",0,13,10, 8,   0x800010,3,8,&garamnd12[177],&garamnd12[179],
   179,  "E",0,13,10, 9,  0x1000010,3,8,&garamnd12[178],&garamnd12[180],
   180,  "T",0,13,10,10,  0x2000010,3,8,&garamnd12[179],&garamnd12[181],
   181,  "R",0,13,10,11,  0x4000010,3,8,&garamnd12[180],&garamnd12[182],
   182,  "Z",0,13,10,12,  0x8000010,3,8,&garamnd12[181],&garamnd12[183],
   183,  "L",3,13,10,13, 0x10000010,3,8,&garamnd12[182],&garamnd12[184],
   184,  "B",3,13,10,14, 0x20000010,3,8,&garamnd12[183],&garamnd12[185],
   185,  "C",3,13,10,15, 0x40000010,3,8,&garamnd12[184],&garamnd12[186],
   186,  "Z",3,13,10,16, 0x80000010,3,8,&garamnd12[185],&garamnd12[187],

   187,  "w",2,14,11, 0, 0x44000008,3,8,&garamnd12[186],&garamnd12[188],
   188,  "F",1,14,11, 1, 0x50000008,3,8,&garamnd12[187],&garamnd12[189],
   189,  "R",1,14,11, 2,     0x8008,3,8,&garamnd12[188],&garamnd12[190],
   190,  "V",0,14,11, 3,    0x10008,3,8,&garamnd12[189],&garamnd12[191],
   191,  "Y",0,14,11, 4,    0x20008,3,8,&garamnd12[190],&garamnd12[192],
   192,  "A",0,14,11, 5,    0x80008,3,8,&garamnd12[191],&garamnd12[193],
   193,  "U",0,14,11, 6,   0x100008,3,8,&garamnd12[192],&garamnd12[194],
   194,  "w",0,14,11, 7,   0x400008,3,8,&garamnd12[193],&garamnd12[195],
   195,  "A",3,14,11, 8,   0x800008,3,8,&garamnd12[194],&garamnd12[196],
   196,  "E",3,14,11, 9,  0x1000008,3,8,&garamnd12[195],&garamnd12[197],
   197,  "G",3,14,11,10,  0x2000008,3,8,&garamnd12[196],&garamnd12[198],
   198,  "T",3,14,11,11,  0x4000008,3,8,&garamnd12[197],&garamnd12[199],
   199,  "R",3,14,11,12,  0x8000008,3,8,&garamnd12[198],&garamnd12[200],
   200,  "K",3,14,11,13, 0x10000008,3,8,&garamnd12[199],&garamnd12[201],
   201,  "V",3,14,11,14, 0x20000008,3,8,&garamnd12[200],&garamnd12[202],
   202,  "X",3,14,11,15, 0x40000008,3,8,&garamnd12[201],&garamnd12[203],
   203,  "Y",3,14,11,16, 0x80000008,3,8,&garamnd12[202],&garamnd12[204],

   204, "fb",0,15,12, 0, 0x44000004,3,8,&garamnd12[203],&garamnd12[205],
   205, "fh",0,15,12, 1, 0x50000004,3,8,&garamnd12[204],&garamnd12[206],
   206,"ffl",0,15,12, 2,     0x8004,3,8,&garamnd12[205],&garamnd12[207],
   207,  "Q",0,15,12, 3,    0x10004,3,8,&garamnd12[206],&garamnd12[208],
   208,  "X",0,15,12, 4,    0x20004,3,8,&garamnd12[207],&garamnd12[209],
   209,  "K",0,15,12, 5,    0x80004,3,8,&garamnd12[208],&garamnd12[210],
   210,  "D",0,15,12, 6,   0x100004,3,8,&garamnd12[209],&garamnd12[211],
   211,  "G",0,15,12, 7,   0x400004,3,8,&garamnd12[210],&garamnd12[212],
   212,  "H",0,15,12, 8,   0x800004,3,8,&garamnd12[211],&garamnd12[213],
   213,  "N",0,15,12, 9,  0x1000004,3,8,&garamnd12[212],&garamnd12[214],
   214,  "O",0,15,12,10,  0x2000004,3,8,&garamnd12[213],&garamnd12[215],
   215,  "m",0,15,12,11,  0x4000004,3,8,&garamnd12[214],&garamnd12[216],
   216,  "w",3,15,12,12,  0x8000004,3,8,&garamnd12[215],&garamnd12[219],
   217,   "",0,15,12,13, 0x10000004,3,8, NULL, NULL,
   218,   "",3,15,12,14, 0x20000004,3,8, NULL, NULL,
   219,  "U",3,15,12,15, 0x40000004,3,8,&garamnd12[216],&garamnd12[220],
   220, "fk",0,15,12,16, 0x80000004,3,8,&garamnd12[219],&garamnd12[221],

   221,  "-",0, 9,13, 0, 0x44000002,3,8,&garamnd12[220],&garamnd12[223],
   222,   "",2,17,13, 1, 0x50000002,3,8,    NULL,  NULL,
   223,  "V",1,17,13, 2,     0x8002,3,8,&garamnd12[221],&garamnd12[224],
   224,  "X",1,17,13, 3,    0x10002,3,8,&garamnd12[223],&garamnd12[225],
   225,  "D",1,17,13, 4,    0x20002,3,8,&garamnd12[224],&garamnd12[226],
   226,  "H",1,17,13, 5,    0x80002,3,8,&garamnd12[225],&garamnd12[227],
   227,  "N",1,17,13, 6,   0x100002,3,8,&garamnd12[226],&garamnd12[228],
   228,  "A",1,17,13, 7,   0x400002,3,8,&garamnd12[227],&garamnd12[229],
   229,  "M",0,17,13, 8,   0x800002,3,8,&garamnd12[228],&garamnd12[230],
   230,  "&",0,17,13, 9,  0x1000002,3,8,&garamnd12[229],&garamnd12[231],
   231,  "m",3,17,13,10,  0x2000002,3,8,&garamnd12[230],&garamnd12[232],
   232,"ffi",3,17,13,11,  0x4000002,3,8,&garamnd12[231],&garamnd12[233],
   233,"ffl",3,17,13,12,  0x8000002,3,8,&garamnd12[232],&garamnd12[234],
   234,  "H",3,17,13,13, 0x10000002,3,8,&garamnd12[233],&garamnd12[235],
   235,  "N",3,17,13,14, 0x20000002,3,8,&garamnd12[234],&garamnd12[236],
   236,  "&",3,17,13,15, 0x40000002,3,8,&garamnd12[235],&garamnd12[237],
   237, "fl",3,17,13,16, 0x80000002,3,8,&garamnd12[236],&garamnd12[238],

   238,  ";",3, 7,14, 0, 0x44000000,3,8,&garamnd12[237],&garamnd12[239],
   239,  "W",1,18,14, 1, 0x50000000,3,8,&garamnd12[238],&garamnd12[241],
   240,   "",0,18,14, 2, 0x80008000,3,8,     NULL, NULL,
   241,  "M",1,18,14, 3, 0x80010000,3,8,&garamnd12[239],&garamnd12[242],
   242,  "*",0,18,14, 4, 0x80020000,3,8,&garamnd12[241],&garamnd12[243],
   243,  "W",0,18,14, 5, 0x80080000,3,8,&garamnd12[242],&garamnd12[244],
   244,  "+",1,18,14, 6, 0x80100000,3,8,&garamnd12[243],&garamnd12[245],
   245,  "M",1,18,14, 7, 0x80400000,3,8,&garamnd12[244],&garamnd12[246],
   246,  "&",1,18,14, 8, 0x80800000,3,8,&garamnd12[245],&garamnd12[247],
   247,  "W",3,18,14, 9, 0x81000000,3,8,&garamnd12[246],&garamnd12[248],
   248,  "=",0,18,14,10, 0x82000000,3,8,&garamnd12[247],&garamnd12[249],
   249, "--",3,18,14,11, 0x84000000,3,8,&garamnd12[248],&garamnd12[250],
   250,  "%",0,18,14,12, 0x88000000,3,8,&garamnd12[249],&garamnd12[251],
   251, "--",0,18,14,13, 0x90000000,3,8,&garamnd12[250],&garamnd12[252],
   252,"...",0,18,14,14, 0xa0000000,3,8,&garamnd12[251],&garamnd12[254],
   253,   "",0,18,14,15, 0xc0000000,3,8,     NULL,         NULL,
   254,  " ",3,18,14,16, 0x80000000,3,8,&garamnd12[252],NULL,



   255,  ".",3, 6, 1,17, 0x80002000,3,8,&garamnd12[33],&garamnd12[256],
   256,  ";",3, 6, 1,18, 0x80002000,3,8,&garamnd12[255],&garamnd12[257],
   257,  "l",3, 6, 1,19, 0x80002000,3,8,&garamnd12[256],&garamnd12[34],

   258,  "J",3, 8, 3,17, 0x80000800,3,8,&garamnd12[67], &garamnd12[259],
   259,  "s",3, 8, 3,18, 0x80000800,3,8,&garamnd12[258],&garamnd12[260],
  260,"\201",1, 8, 3,19, 0x80000800,3,8,&garamnd12[259],&garamnd12[261],
  261,"\204",1, 8, 3,20, 0x80000800,3,8,&garamnd12[260],&garamnd12[262],
  262,"\211",0, 8, 3,21, 0x80000800,3,8,&garamnd12[261],&garamnd12[263],
  263,"\210",0, 8, 3,22, 0x80000800,3,8,&garamnd12[262],&garamnd12[264],
  264,"\207",0, 8, 3,23, 0x80000800,3,8,&garamnd12[263],&garamnd12[265],
  265,"\205",0, 8, 3,24, 0x80000800,3,8,&garamnd12[264],&garamnd12[266],
  266,"\203",0, 8, 3,25, 0x80000800,3,8,&garamnd12[265],&garamnd12[68],

   267,  "2",2, 9, 5,17, 0x80000200,3,8,&garamnd12[101],&garamnd12[268],
   268,  "5",2, 9, 5,18, 0x80000200,3,8,&garamnd12[267],&garamnd12[269],
   269,  "0",2, 9, 5,19, 0x80000200,3,8,&garamnd12[268],&garamnd12[102],

   270,  "v",3,10, 7,17, 0x80000080,3,8,&garamnd12[135],&garamnd12[271],
   271,  "o",3,10, 7,18, 0x80000080,3,8,&garamnd12[270],&garamnd12[136],

   272,"\214",0, 5, 0, 17,   0x404000,3,8, &garamnd12[16], &garamnd12[273],
   273,"\215",0, 5, 0, 18,   0x404000,3,8, &garamnd12[272], &garamnd12[274],
   274,"\241",0, 5, 0, 19,   0x404000,3,8, &garamnd12[273], &garamnd12[17]


};

struct rccoord pos;

struct rijtje {
    struct m_type *p;
    int n;
} ry1,ry2,ry3,ry4;

/* ligaturen ook in een ring */

struct ligatuur {
    char lig[4];
    unsigned char rij;
    unsigned char kol;
    unsigned char w;
}  ligtabel[25][4];

char ncols[17][3] = {"NI ","NL ","A  ","B  ","C  ","D  ",
		     "E  ","F  ","G  ","H  ","I  ","J  ",
		     "K  ","L  ","M  ","N  ","O  " };

unsigned int wedge[16];

struct rccoord pos;



/* globale variabelen */

FILE *infile;
FILE *outfile;
FILE *center;         /* filehandle centraal file    */
FILE *matrixfl;       /* filehandle voor matrix file */
FILE *textfile;       /* filehandle voor textfile    */
FILE *monocode;       /* filehandle voor gietcode    */

/* globale pointers */

struct m_type *curs        = NULL ;  /* geeft plaats in de regel aan */
struct m_type *einde_regel = NULL ;
struct m_type *begin_regel = NULL ;
struct m_type *matrix      = NULL ;  /* begin rij matrix-records */
struct m_type *eindmatrix  = NULL ;  /* laatste in de rij van matrix-records */
struct m_type *ligaturen   = NULL ;  /* begin rij ligaturen-records */
struct m_type *endligtrn   = NULL ;  /* laatste in de rij */

struct m_type * verwijs[4][256];      /* verwijzen naar de matrix-records */
struct m_type * ligatures[50];

unsigned int aantallen[32];
unsigned char uitvul[2];  /* uitvulcijfers */

char  cursorbuff[7] = { '\0', '\0', '\0', '\0', '\0', '\0', '\0'};
char  bufferstr[256];
char  regelbuff[80];

char  string[29]  = { 'a','b','c','d','e', 'f','g','h','i','j',
		      'k','l','m','n','o', 'p','q','r','s','t',
		      'u','v','w','x','y', 'z', '\xd','\xa','\0' };



/* ********* central memory of the program *** */

int bezet[16][37];

struct m_type opslag[1500];


/* ********* general functions definitions ***************** */

char aandacht(int r,int k, char buf[]);
unsigned int vraagkolom(int r, int k);
void cint(char *b,int ii, int p);
void creal(char *b, float real, int p, int f, int m);
void creal2(char *b, float real, int p, int f, int m);
void cdubbel(char *b, double real, int p, int f, int m);

void hoofdmenu( void );
void main2();
int  main3( void );
void maintest();

void textmain( void );

/* vanaf hier : */

void cls(void);
void clsblauw(void);
void colorprint(int r, int k, int soort, char *buf );
void print_at(int rij, int kolom, char *buf);
int  genereer(int x,char *buf);


unsigned int o_central( char stuur );
unsigned int _lees_matrix();

unsigned tooncur(int soort, char * s, int lim );                /* toon cursor op actuele plaats */

unsigned int _schrijf_matrix();
/* show matrix at row r, colom k */
void weergeven(struct m_type *p, int n, int r, int k);
unsigned int _change_matrix();
unsigned int _defa_ult_matrix();
unsigned int _new_matrix();
unsigned int _edit();

void lees_matrijs(struct m_type * mat, char *buf);

void wissen_matrix(void);
void dispma( struct m_type *cur );
unsigned int dispmat();


void dispbuiten();  /* display buitenmatrijzen */

void disp_buit(int rij); /* display buiten matrijzen in rij */

void disp_type(struct m_type *p );

void data_copy(struct data_matrix *dest, const struct data_matrix *source);
void copypp(struct m_type *dest, struct m_type *bron);
void ber_u1u2(unsigned int set, unsigned int ldikte, int toevoeg);

int filesopenen();
int filesluiten();
unsigned lezen();

unsigned get_line2(int r, int k, char *s , unsigned lim);
unsigned get_line(char *s , unsigned lim);
void split_str(char *b, char *l, char *r, unsigned int k);

void cursorpos(int rij, int kol, int soort,int aanuit);

float l2_real(float min, float max, int r, int k);
int   l2_int (int min, int max, int r, int k);
unsigned char inlezen_set(int r, int k);



/******************************************/
/*  function-declarations matrix- storage */
/******************************************/

unsigned int matrix_inlezen(void);    /* read matrix */



/***************************************************************/
/*   functions to control the pointer-arithmatic of the editor */
/***************************************************************/

void gereedmaken_opslag(void);          /* init storage of records */

/* gereedmaken_opslag
     = take the memmory fysically in possession
     the compiler, uses the memmory is a very dynamical way
     and you may find the the memmory is spoiled
     It costs some performance, but secures a good behaviour of
     the program
*/

struct m_type * vrijmaken(void);        /* get record from storage */
void clear_record(struct m_type * p);   /* cleans the record       */
void terugzetten(struct m_type *px);    /* put record in storage   */
void show_voorraad(unsigned int start, unsigned int aantal, int r);

struct m_type * start_rij( char c[] );
	  /* start de rij: eerste char in rij   */

struct m_type * achtervoegen(struct m_type *px, struct m_type * einde);
	  /* add record to the line, at the end */
/*
     in de rij :
	  adds a record , behind the cursor, en moves the cursor
	  to the new record
*/

void in_de_rij(struct m_type * cur, struct m_type * px);
struct m_type * del ( struct m_type * cur) ;
	/* delete record at the back of the cursor */

struct m_type * backsp( struct m_type * cur);
	/* delete record, the cursor points to */

struct m_type * voeg_toe( char *c, struct m_type * cursor );
struct m_type * inkorten( struct m_type *strt);
void show_rij( struct m_type *cur , int direct );


/* * * * * * * * * * * * * * * * * * * * * * * */
/*                                             */
/*          uitwerkingen functions             */
/*                                             */
/* * * * * * * * * * * * * * * * * * * * * * * */

/*  vraagkolom : vraagt in lettercode de kolomnaam van de
   matrijs in de matrix
   ni,nl,a,b,c,d,e,f,g, h,i, j, k, l, m, n, o,
   1  2  3 4 5 6 7 8 9 10 11 12 13 14 15 16 17
   */

unsigned int vraagkolom(int r, int k)
{
    int  c,i;
    char s[8];
    char buff[8];
    int lim = 3, rk=0;

    do {
	do {
	   sprintf(buff,"   ");
	   colorprint(r,k,0,buff);
	   _settextposition(r,k);
	   _settextcursor( DOUBLEUNDERLINE );
	   _displaycursor( _GCURSORON );
	   for (i=0 ; i< lim-1 && (c=getchar())!=EOF && c!='\n';i++){
	      if ((c>='A') && (c<='Z') ) c = c - 'A' + 'a';
	      /* ANSI version of: c = tolower(c); */
	      s[i]= c;
	   }
	   if (c=='\n') { s[i]=c; i++; } s[i]='\0';
	} while (s[0] == '\0' /* 10 */ );
	if (s[0] == 'n' ) {
	   if (s[1] == 'i') {
	      rk = 1;
	   } else {
	      if (s[1] == 'l') {
		 rk = 2;
	      } else {
		 rk = s[0] +3 - 'a';
	      }
	   }
	} else {
	   if (s[0] >= 'a' && s[0] <= 'o') {
	      rk = s[0] + 3 - 'a' ;
	   }
	}
    } while ( ! rk );
    return( rk );
}

unsigned tooncur(int soort, char * s,int lim) {

    int c,i;

    _settextcursor( soort );
    _displaycursor( _GCURSORON );

    for (i=0;i<lim-1 && (c=getchar())!=EOF && c!='\n';i++){
       s[i]=c;
    }
    if (c=='\n') { s[i]=c; i++; } s[i]='\0';
    return (i);

}

void cint(char *b, int ii, int p)
{
    int bi, i,k,n=0;

    bi = ii;

    k=bi;
    if (k<0) {
       b[p-2]='-';
       k  *= -1;
       bi *= -1;
    }
    while (k>0) {
       n++; k /=10;
    }
    for (i=0, k=bi ;i<n;i++){
       b[p+n-i-2]= ( k % 10 )+'0';
       k /= 10;
    }
}

void creal(char *b, float real, int p, int f, int m)
{
    int i,k,n=0,fi,n2,q;
    float man,rr;

    rr = real;
    q=p-2;
    if (rr < 0) {
       b[q]='-';
       rr *= -1.0;
    }

    fi = (int) rr;
    man = rr - (float) fi;
    for(i=0;i<m;i++) man *=10;
    man += .5;        /* afronden */
    k=fi;             /* first the integer part */
    while (k>0) {
	n++; k /=10;
    }
    q = p+n-2;
    for (i=0,k=fi;i<n;i++){
       b[q-i]= (k % 10) +'0';
       k /= 10;
    }
    q++;
    b[q++]='.';
    for (i=0;i<m;i++){
       b[q+i]='0';
    }
    fi = (int) man;
    k=fi;
    n2=0;
    while (k>0) {
       n2++; k /=10;
    }
    for (i=0,k=fi;i<n2;i++){
       b[p+n+m-i-1]= ( k % 10 )+'0';
       k /= 10;
    }
}

void creal2(char *b, float real, int p, int f, int m)
{
    int i,n=0,n2, q;
    int fi,k;
    float man,rr;

    rr = real;
    q=p-2;
    if (rr < 0) {
       b[q]='-';
       rr *= -1.0;
    }

    fi = (int) rr;
    man = rr - (float) fi;
    for(i=0;i<m;i++) man *=10;
    man += .5;         /* afronden */

    k=fi;              /* first the integer part */
    while (k>0) {
	n++; k /=10;
    }
    q += n ;
    for (i=0,k=fi;i<n;i++){
       b[q-i]= (k % 10) +'0';
       k /= 10;
    }
    q++;  b[q++]='.';
    for (i=0;i<m;i++){
       b[q+i]='0';
    }
    fi = (int) man; k=fi; n2=0;
    while (k>0) {
       n2++; k /=10;
    }
    for (i=0,k=fi;i<n2;i++){
       b[p+n+m-i-1]= ( k % 10 )+'0';
       k /= 10;
    }
}


void cdubbel(char *b, double real, int p, int f, int m)
{
    int i,n=0,n2, q;
    long fi,k;
    double man,rr;

    rr = real;
    q=p-2;
    if (rr < 0) {
       b[q]='-';
       rr *= -1.0;
    }

    fi = (long) rr;
    man = rr - (double) fi;
    for(i=0;i<m;i++) man *=10;
    man += .5;         /* afronden */

    k=fi;              /* first the integer part */
    while (k>0) {
	n++; k /=10;
    }
    q += n ;
    for (i=0,k=fi;i<n;i++){
       b[q-i]= (k % 10) +'0';
       k /= 10;
    }
    q++;  b[q++]='.';
    for (i=0;i<m;i++){
       b[q+i]='0';
    }
    fi = (long) man; k=fi; n2=0;
    while (k>0) {
       n2++; k /=10;
    }
    for (i=0,k=fi;i<n2;i++){
       b[p+n+m-i-1]= ( k % 10 )+'0';
       k /= 10;
    }
}

void hoofdmenu(){
      char c;
      char __command;
      char __stoppen = 0 ;
      char __matrix  = 0 ;
      char __new = 2;

	   /* new kan 3 waarden hebben:
		 0: oud file
		 1: wel een nieuw file
		 2: enkel basisgegevens lezen in centraal file
		 we starten met dit laatste...
	   */
      int __files   = 0 ;
      char __changes = 0 ;


      _clearscreen( _GCLEARSCREEN ); /* cls(); */
      printf(" monotype-programma versie 25-2-2002 \n\n");
      do {

	  do {
	      __files = o_central( '0' );

	      _clearscreen( _GCLEARSCREEN ); /* cls */

	      printf(" Monotype-programma \n\n");
	      printf(" aanwezig %4d matrix-files \n\n",__files);
	      printf("  new matrix     : n  \n");
	      if ( __files ) {
		 printf("  read matrix    : r  \n");
	      }
	      if (__matrix ){
		 printf("  change matrix  : c  \n");
		 printf("  edit text      : e  \n");
		 printf("  letterkast     : l  \n");
		 printf("  file gieten    : g  \n");
	      }
	      printf("\n");
	      printf("  stop program   : s  \n");

	      printf("\n");
	      printf(" geef command :");

	      __command = getchar();
	      __command = tolower( __command );


	  } while ( ( __command != 'r') && /* read matrix   */
		    ( __command != 'c') && /* change matrix */
		    ( __command != 'd') && /* default matrix */
		    ( __command != 'w') && /* write matrix  */
		    ( __command != 'n') && /* new matrix    */
		    ( __command != 'e') && /* edit text     */
		    ( __command != 'l') && /* letterkast    */
		    ( __command != 'g') && /* file gieten   */
		    ( __command != 's') ); /* stop program  */

	    switch (__command ) {
		case 'd' : /* default matrix: garamond 12 pnt */
		  __matrix = _defa_ult_matrix();
		  break;
		case 'r' : /* lezen mag als er gelezen kan worden */
		  if ( __files )
		      __matrix = _lees_matrix();
		  break;
		case 'w' :
		  if (  __new == 1 )
		     __files = o_central( 'n') ;
		  if ( __changes )
		     o_central('a');
		     _schrijf_matrix();
		  break;
		case 'n' : /* een nieuwe mag altijd */
		  __matrix = _new_matrix();
		  _schrijf_matrix(); /* filenummer meegeven */
		  __new = __matrix;
		  break;
		case 'e' : /* edit file */
		  if ( ( __files ) && (__matrix ) ) _edit();
		  break;
		case 'c' : /* veranderen van een matrix */
		  if ( __matrix )
		     __changes = _change_matrix(); /* filenummer meegeven */
		     __new = 0;
		     _schrijf_matrix();
		  break ;
		case 's' :
		  break;
	    }

	    /* valide : als aantal files > 0 :
		dan mag een matrix gelezen worden */
	    /* als aantal files = 0 of != 0 :
		er mag een nieuwe matrix gemaakt worden */
	    /* change kan enkel als er een matrix is */
	    /* wegschrijven kan enkel als er veranderingen in de
			matrix zijn gemaakt */


      } while (__command != 's');
      /* sluit alle files */
} /* einde hoofdmenu */

/****************************************************************/
/*                                                              */
/*    maintest: testing pointer-routines last version: 3 feb    */
/*                                                              */
/****************************************************************/

void maintest ( void )
{


     int aantalgelezen=0;

     struct m_type *pp          = NULL;
     struct m_type *cursor      = NULL;
     struct m_type *start_regel = NULL;

     int i,j;
     char c, cc[3]="";

     printf("Maintest \n");

     gereedmaken_opslag( );

     printf("Main \n");

     for (i=0; (c=string[i]) != '\0' ; i++) {
	switch (c) {
	   case 10 : printf("LF"); break;
	   case 11 : printf("VT"); break;
	   case 12 : printf("FF"); break;
	   case 13 : printf("CR"); break;
	   default : printf("%c", c);
	}
     }
     getchar();

     /* show_voorraad(495,540,1); getchar();*/
     /* show_voorraad(35,540,-1); getchar();*/

     start_regel = start_rij(string);
     aantalgelezen ++;
     /* show_rij( start_regel , 1); */
     /* 1e stuk */

     cursor = start_regel ;
     printf("vullen van de rij\n");
     for (i=1;i<=27;i++){
       cc[0]=string[i];
       cursor = voeg_toe( cc , cursor );
       printf(" %3d ", cursor -> ligature[0]);
       einde_regel = cursor;
       aantalgelezen ++;
     }
     getchar();

     show_rij( einde_regel , -1 );
     show_rij( start_regel, 1);
     /* show_voorraad(480,50,1); getchar();   */
     /* show_voorraad(35,50,-1); getchar();   */

     /* 2e stuk */

     pp = start_regel;
     for (i=0;i<=4;i++) pp = pp -> _next;
     printf("testen delete vanaf positie %3d\n", pp -> naam );
     del ( pp );
     show_rij( einde_regel , -1 );
     show_rij( start_regel, 1);
     /* show_voorraad(495,50,1); getchar(); */
     /* show_voorraad(35,50,-1); getchar(); */
     pp = start_regel;
     /* for (i=0;i<=1;i++) pp = pp -> _next; */
     printf("testen delete vanaf positie %3d\n", pp -> naam );
     del ( pp );
     show_rij( einde_regel, -1 );
     show_rij( start_regel, 1);
     /* show_voorraad(495,50,1); getchar();     */
     /* show_voorraad(35,50,-1); getchar();     */

     /* 3e stuk */
     pp = start_regel;
     start_regel = inkorten(pp);
     if (start_regel == NULL) einde_regel = NULL;
     pp = start_regel;
     start_regel = inkorten(pp);

     show_rij( einde_regel , -1 );
     show_rij( start_regel, 1);
     show_voorraad(495,50,1); getchar();
     show_voorraad(35,50,-1); getchar();

     printf("nu gaan we backspace testen ");
     getchar();

     /* 4e stuk */

     cursor = start_regel;
     if (cursor ->_next != NULL)
	  cursor = cursor -> _next;
     show_rij( einde_regel, -1 );
     show_rij( start_regel, 1);
     printf("startregel = %3d ",start_regel ->naam);
     getchar();

     cursor = backsp( cursor);

     printf("startregel = %3d ",start_regel -> naam);
     getchar();

     /* #######      del ( cursor ); */

     show_rij( einde_regel, -1 );
     show_rij( start_regel, 1);
     show_voorraad(495,50,1); getchar();
     show_voorraad(35,50,-1); getchar();
     getchar();
     /* 5e stuk */
}

void main2()
{
    int c, newrec;
    size_t recsize = sizeof( filerec );
    FILE *recstream;
    long recseek;

    /* Create and open temporary file. */
    recstream = tmpfile();

    /* Write 10 unique records to file. */
    for( c = 0; c < 10; c++ )
    {
	++filerec.integer;
	filerec.doubleword *= 3;
	filerec.realnum /= (c + 1);
	strrev( filerec.string );

	fwrite( &filerec, recsize, 1, recstream );
    }

    /* Find a specified record. */

    do
    {
	printf( "Enter record betweeen 1 and 10 (or 0 to quit): " );
	scanf( "%d", &newrec );

	/* Find and display valid records. */
	if( (newrec >= 1) && (newrec <= 10) )
	{
	    recseek = (long)((newrec - 1) * recsize);
	    fseek( recstream, recseek, SEEK_SET );

	    fread( &filerec, recsize, 1, recstream );

	    printf( "Integer:\t%d\n", filerec.integer );
	    printf( "Doubleword:\t%ld\n", filerec.doubleword );
	    printf( "Real number:\t%.2f\n", filerec.realnum );
	    printf( "String:\t\t%s\n\n", filerec.string );
	}
    } while( newrec );

    /* Starting at first record, scan each for specific value. The following
     * line is equivalent to:
     *      fseek( recstream, 0L, SEEK_SET );
     */
     /*
      rewind( recstream );

      do
      {
	fread( &filerec, recsize, 1, recstream );
      } while( filerec.doubleword < 1000L );

      recseek = ftell( recstream );
      / * Equivalent to: recseek = fseek( recstream, 0L, SEEK_CUR ); * /
      printf( "\nFirst doubleword above 1000 is %ld in record %d\n",
	      filerec.doubleword, recseek / recsize );
    */
    /* Close and delete temporary file. */
    rmtmp();
}


void textmain(void)
{
    short blink, fgd, oldfgd, color;
    long bgd, oldbgd;
    struct rccoord oldpos;
    char buffer[20];
    int i;

    /* Save original foreground, background, and text position. */
    oldfgd = _gettextcolor();
    oldbgd = _getbkcolor();
    oldpos = _gettextposition();
    clsblauw();
    getchar();

    _clearscreen( _GCLEARSCREEN );

    /* First time no blink, second time blinking. */
    blink = 0; /* blink <= 16; blink += 16 ) */
    /*{*/

	/* Loop through 8 background colors. */
    bgd = 1;

    _setbkcolor( bgd );
    bgd = 2;
     _setbkcolor( bgd );
     _clearscreen( _GCLEARSCREEN );

    getchar();
    bgd = 3;
    _setbkcolor( bgd);
    _clearscreen( _GCLEARSCREEN );

    getchar();
    bgd = 4;
    _setbkcolor(bgd);
    _clearscreen( _GCLEARSCREEN );

    getchar();
    bgd = 5;

    _setbkcolor( bgd );
    _clearscreen( _GCLEARSCREEN );
    getchar();
    clsblauw();
    getchar();

       _settextposition( i , 1 );
       _settextcolor( 7 );
       sprintf(buffer, "Back: %d Fore:", bgd );
       _outtext( buffer );

	    /* Loop through 16 foreground colors. */
	    for( fgd = 1; fgd < 16; fgd++ )
	    {
		/* _settextcolor( fgd + blink );*/
		sprintf( buffer, " %2d ", fgd + blink );
		colorprint( fgd-10, 10, fgd-11, buffer );
		/* _outtext( buffer );                    */
	    }

    /*}*/
    getch();

    /* Restore original foreground and background. */
    _settextcolor( oldfgd );
    _setbkcolor( oldbgd );
    _clearscreen( _GCLEARSCREEN );
    _settextposition( oldpos.row, oldpos.col );
}

void cls() {
    _clearscreen( _GCLEARSCREEN );
}

void clsblauw()
{
     long bgd=1;

     _setbkcolor( bgd );
     _settextcolor(15);
     _clearscreen( _GCLEARSCREEN );
}

void colorprint(int r, int k, int soort, char *buf )
{
       _settextposition( r,k );
       switch (soort) {
	   case 0 :
	      _settextcolor( 15 );
	      break;
	   case 1 :
	      _settextcolor( 13 );
	      break;
	   case 2 :
	      _settextcolor( 14 ); /* 12 = paars */
	      break;
	   case 3 :
	      _settextcolor( 11 ); /* lichtblauw */
	      break;
       }
       _outtext( buf );
       _settextcolor( 1 );
}

void print_at(int rij, int kolom, char *buf)
{
     _settextposition( rij , kolom );
     _outtext( buf );
}

int  genereer(int x,char *buf)
{
    char fnaam[30] = "a:\\mat00000.mat";  /* d:\\monotype\\mat00000.mat" */
    char buffer[30];
    int l,k,i,j;
		   /* 01 2345678901234567890123
		   l= 12 3456789011234
		   */
    l = strlen(fnaam);
    sprintf(buffer,"l = %3d ",l);

    strcat(buffer,fnaam);
    _outtext(buffer);
    getchar();
    k=l-5;
    while ( x > 0){
	 fnaam[k--] = (x % 10) + '0';
	 x /= 10;
	 sprintf(buffer," naam file :");
	 strcat(buffer,fnaam);
	 _outtext(buffer);
	 getchar();
    }
    sprintf(buffer," naam file :");
    strcat(buffer,fnaam);

    strcpy(buf,fnaam);
    getchar();
    return(strlen(fnaam));
}

void disp_buit(int ry)
{
    int i,r,k,r2;
    struct m_type * ma;

    char buf[80];

    ry1.p = NULL;   /* struct rijtje ry1.p
			wijst naar begin van een rij records
		     */
    ry1.n = 0;      /* aantal buitenmatrijzen in het rijtje */

    strcat(buf ,"    ");
    cint(buf,ry,2);

    sprintf(buf," %2d ",ry);
    colorprint(22,1,0,buf);
    r2= ry-1;
    for (ma = matrix; ma != NULL ; ma = ma ->_next) {
	 r = ma -> row;
	 if (r == r2) {
	     k = ma -> col;
	     if (k>16) {
		if (ry1.p == NULL) ry1.p = ma;
		ry1.n ++;

		sprintf(buf,"%2d",ry1.n);
		colorprint(21,(k-17)*4+5,0,buf);
		for (i=0;i<3;i++) buf[i]=ma -> ligature[i] ; buf[3]='\0';
		colorprint(22,(k-17)*4+6,ma ->kind,buf);
	     }
	 }
    }
}


void copypp(struct m_type *dest, struct m_type *bron)
{
     int i,j;

     for(i=0;i<3;i++) dest -> ligature[i] = bron->ligature[i];
     dest -> kind  = bron -> kind;
     dest -> width = bron -> width;
     dest -> row   = bron -> row;
     dest -> col   = bron -> col;
     dest -> code  = bron -> code;
     dest -> u[0]  = bron -> u[0];
     dest -> u[1]  = bron -> u[1];
     dest -> _fore = NULL;
     dest -> _next = NULL;
}

void disp_type(struct m_type * p)
{
     int i,l;
     l = strlen(p->ligature);
     if (l ){
	for (i=0;i<l;i++) printf("%1c",p->ligature[i]);
     } else {
	printf("   ");
     }
     printf(" s=%2d w=%2d rij %2d kolom %2d ",p->kind,p->width,p->row,p->col);
     printf(" code %x9 u = %2d/%2d ",p -> code, p -> u[0], p -> u[1]);
     getchar();
}

unsigned int o_central(char stuur )
	/* stuur = '0' => lees aantal matrix-files uit 1e record
	   stuur = 'n' => nieuw matrix-file
	   stuur = 'o' => opzoeken oud matrix-file
	   stuur = 'a' => aanpassen oud matrix-file

	   matrix-file: centrale gegevens opslaan
	   matrix-file: kiezen matrix uit aanwezige matrices
	*/

{
    int c, newrec, antw;
    size_t recsize = sizeof( centerrec );
    long recseek;
    char fnaam[]= "a:\\mat00000.mat";  /* d:\\monotype\\mat00000.mat" */
		/* 01 2345678901234567890123
		l= 12 3456789011234
		*/


    int records,  /* aantal matrix-files */
	  x,i,j,k,a,amax ;

    int filenummer;

    printf("centraal file lezen ");

    switch (stuur ) {
       case '0' : /* lees aantal matrix-files */
	 filenummer = 0;
	 if ( (center = fopen("a:\\centerfl.mon","r")) == NULL)
	 { /* file bestond nog niet, creat file + schrijf eerste record */
	     printf("het file bestond nog niet ");
	     getchar();
	     center = fopen("a:\\centerfl.mon","a+");
	     centerrec.aantal = 0; /* = aantal files */
	     /* schrijf record nul */
	     records = 0;
	     fseek(center,0L,SEEK_SET); /* aan het begin zetten */
	     fwrite( &centerrec, recsize, 1, center );
	 } else {
	     /* centerfile bestond al: lees in eerste record */
	     recseek = (long)(( filenummer ) * recsize);
	     fseek( center , recseek, SEEK_SET );
	     fread( & centerrec, recsize, 1, center );
	     printf( "aantal matrix-files  %d\n", centerrec.set );
	     records = centerrec.aantal;
	 }
	 break;
       case 'n' : /* nieuw matrix-file schrijven */
	 printf(" nieuwe matrix-file wegschrijven ");
	 printf("nieuw file: record bijschrijven \n");
	 printf("nieuw file openen en wegschrijven ");
	 getchar();
	 records ++; x = records;
	 k = strlen(fnaam) - 4;
	 while ( x > 0){
	     fnaam[k--] = (x % 10) + '0';
	     x /= 10;
	     printf(" naam file %c ",fnaam );
	     getchar();
	 }
	 /* filenaam in centerrec zetten */
	 x=strlen(fnaam);
	 for (i=0;i<x;i++){
	    centerrec.filenaam[i]=fnaam[i];
	 }

	 fseek( center, 0L, SEEK_END );  /* aan het eind zetten */
	 fwrite( &centerrec, recsize, 1, center );
	 matrixfl = fopen (fnaam,"w");   /* openen matrixfile */


	   /*
	     nieuw record wegschrijven in centraal file
	     filenaam genereren
	     matrix-file openen
	   */
	 break;
       case 'o' : /* opzoeken data eerder weggeschreven files */
	 if (records>=0 ) {
	   a=1;
	   do {
	     amax = a+9; if (amax > records) amax = records;
	     do {
	       _clearscreen( _GCLEARSCREEN );
	       printf("kiezen uit %3d files ",records);
	       for (i=a;i<=amax;i++) {
		 recseek = (long)(( i ) * recsize);
		 fseek( center , recseek, SEEK_SET );
		 fread( & centerrec, recsize, 1, center );
		 printf("file %3d   %c ", i , centerrec.charname[40]);
		 printf("   set %5.2f corps %4.1f pica %4.1f didot ",
			 (float) (centerrec.set)*0.25 ,
			 (float) (centerrec.corps[0])*0.5,
			 (float) (centerrec.corps[1])*0.5 );
		  /* lees record */
		  /* display     */
	       }
	       printf("\nkies filenummer");
	       get_line(regelbuff,5);
	       antw = atoi(regelbuff);
	       printf("gekozen : %3d ",antw);
	       getchar();
	     } while ((a<=antw)&&(antw<=amax)&&(antw!=0));
	     a = amax + 1 ;
	     if ( amax == records ) break;
	   } while ((1<= antw ) && (antw <=records) );
	 } else {
	   printf(" er zijn geen files \n");
	   getchar();
	 }
	 /*
	   lees de eerste 10 records:
	     display de namen letterss + corps
	     maak keuze mogelijk
	 */
	 getchar();
	 if (antw !=0) {
	    filenummer = antw;
	    recseek = (long)(( filenummer ) * recsize);
	    fseek( center , recseek, SEEK_SET );
	    fread( & centerrec, recsize, 1, center );
	    printf("openen filenaam %c \n", centerrec.filenaam );
	    if (matrixfl = fopen(centerrec.filenaam,"r+")){
	       /* lezen matrixfile */
	       /* centerrec.aantal */
	    } else{
	       printf("file kon niet worden geopend ");
	       getchar();
	    }
	 }
	 /* kiezen tussen al wat er al is */
	 /* lees uit de eerste tien of minder de namen van de matrices */
	 /* openen matrix-file */
	 /* lezen */

	 break;
       case 'a' : /* aanpassen oud matrix-file */
	 printf(" matrix-file aanpassen ");
	 getchar();
	 break;

	 /*
	 struct data_matrix {
		char charname[40];         / * naam letter * /
		char nummers[15];          / * monotype aanduidingen * /
		unsigned int  set;         / * width largest character in pica-points * 4  * /
		unsigned int  corps[2];    / * corps engels / didot in 1/2 punten * /
		char charwedge[8];         / * monotype aanduiding wig  * /
		unsigned int cwedge[16];   / * indeling wig * /
		char filenaam[30];       / * filenaam van matrix-file * /
		unsigned int aantal;     / * aantal letters totaal * /
	 } centerrec ;
	 * /
	 recseek = (long)((filenummer) * recsize);
	 fseek( center, recseek, SEEK_SET );
	 fread( &centerrec, recsize, 1, center );

	 printf( "Naam letter      : %c \n", centerrec.charnaam );
	 printf( "Monotype nummers : %c \n", centerrec.nummers );
	 printf( "set              : %6.2f \n", S = float (centerrec.set) * 0.25);
	 printf( "corps engels %4.1f didot %4.1f \n",float(centerrec.corps[0])*.5,
						    float(centerrec.corps[0])*.5 );
	 printf( "wig-indeling : ");
	 for (i=0;i<14;i++) printf(" %2d,",centerrec.cwedge[i]);
	 printf( "\n aantal records : %4d \n",centerrec.aantal);
	 printf( " filenaam : %c \n",centerrec.filenaam);
	 getchar();

	*/
    } /* einde switch */
    fclose( center );
    return(records);
}

unsigned int _lees_matrix(){
   printf(" _lees_matrix vanaf harde schijf ");
   getchar();
   /* eerst aanroep o_central :
       openen datafile,
       filenummer van het file
       filehandle nodig voor het wegschrijven...
       aantal records komt later
   */
   return (1);
}


void cursorpos(int rij, int kol, int soort, int aanuit)
{
     /* streepje = insert    = 7   */
     /* blokje   = overwrite = 772 */

     _settextposition( rij , kol );
     _settextcursor(soort);
     _displaycursor( (aanuit ) ? _GCURSORON : _GCURSOROFF );
}


unsigned int _schrijf_matrix()
{
   struct m_type *cur;
   char fnaam[30];
   size_t recsize = sizeof( struct m_type );
   int i,x,n=0;

   printf(" _schrijf_matrix op schijf weg :");
   getchar();
   /* openen file als het nog niet open is */
   /* */

   for (i=0; (i<30) && (centerrec.filenaam[i] != '\0') ;i++){
      fnaam[i] = centerrec.filenaam[i]=fnaam[i];
   }
   if ( ( matrixfl = fopen (fnaam,"w") ) == NULL) {
       printf("File kon niet worden geopend ");
       getchar();   /* openen matrixfile */
   } else {
       printf("File geopend voor schrijven ");
       getchar();
       for (cur = matrix ; cur != NULL ; cur = cur -> _next ){
	  /* schrijf cur weg */
	  fseek(matrixfl, 0L,SEEK_END );
	  fwrite( cur, recsize,1,matrixfl);
	  printf("weggeschreven record %4d \n",n++);
	  /* getchar(); */
       }
   }
   fclose(matrixfl);
   return(1);
}


unsigned int _edit(){
   printf(" _edit ");
   getchar();

   return(1);
}

void lees_matrijs(struct m_type * pp, char *buf)
{
   int i,j,rij,kolom,iantw,n;
   unsigned int wig, cset;
   char c;
   unsigned char uu[2]= { 3,8 } ;
   unsigned long cc;
   char buff[40];
   struct rccoord opos;

   sprintf(buff,"lees matrijs ");
   colorprint(2,1,0,buff);


   n = strlen(buf);
   for (i=0;i < n;i++){ pp -> ligature[i]=buf[i]; }
   sprintf(buff," soort \? romein = 0, italic = 1 klein kap = 3, vet = 4");
   colorprint(4,1,0,buff);
   opos = _gettextposition();
   pp -> kind = l2_int(0,4,opos.row, opos.col);
   if (pp -> row == -1) { /* indien -1 niet lezen !! */
       sprintf(buff,"in welke rij  ");
       colorprint(5,1,0,buff);
       opos = _gettextposition();
       rij =l2_int(1,MAXRIJ,opos.row,opos.col) - 1 ;
       pp -> row = rij;
   }
   if (pp -> col == -1) { /* indien -1 niet lezen !! */
       sprintf(buff,"in welke kolom ");
       colorprint(6,1,0,buff);
       /* letteraanduiding kolom moet ook werken */
       opos = _gettextposition();
       pp -> col = l2_int( 1, 18, opos.row, opos.col) -1;
       /* het programma zelf laten zoeken welk nummer een
       buitenmatrijs zal krijgen */
   }
   /* pp -> row = rij ; pp -> col = kolom ; */

   wig = centerrec.cwedge[rij];

   /* uu[0]=3; uu[1]=8; */

   sprintf(buff,"dikte letter   ");
   colorprint(7,1,0,buff);
   opos = _gettextposition();
   iantw = l2_int(0,23,opos.row,opos.col);
   if ( ! iantw ) iantw = wig ;
   if (iantw != wig ) {
	/* uitvulling berekenen */
	ber_u1u2(cset, wig , iantw - wig );
	uu[0] = uitvul[0] ;  uu[1] = uitvul[1];
	cc |= _Snaald;
   } else {
	uu[0] = 3; uu[1] = 8;
   }
   pp -> code = cc;
   pp -> u[0] = uu[0];
   pp -> u[1] = uu[1];
}

void wissen_matrix(void) /* als matrix gevuld is: wissen oude matrix */
{
    int i,j;
    char buf[83];

    if (matrix == &garamnd12[0]) {

       return;
    } else {
       /*
       strcpy(buf,"Wissen oude matrix ");
       pos = _gettextposition();
       colorprint(pos.row,pos.col,0,buf);
       pos = _gettextposition();
       cursorpos(pos.row, pos.col, OVERSCHRIJVEN, AAN );
       getchar();
       */
    }
    /* wissen verwijstabel */
    for (i=0;i<=3;i++) {
       for (j=0;j<=255;j++) {
	  verwijs[i][j] = NULL;
       }
    }
    /* wissen bezet-tabel */
    for (i=0;i<16;i++) {
	for (j=0;j<37;j++) bezet[i][j] = 0;
    }
    /* controleren of er al een matrix in het geheugen staat
	dan is matrix != eindmatrix
    */
    while ( matrix  != NULL) {
       matrix = inkorten ( matrix );
    }
    eindmatrix = NULL;

    while ( ligaturen != NULL) {
       ligaturen = inkorten(ligaturen);
    }
    endligtrn = NULL;
}

void dispma( struct m_type *cur )
{
     int i,r,k;
     char buf[5];

     r = cur -> row;
     k = cur -> col;

     for (i=0;i<3;i++) buf[i]= cur -> ligature[i] ; buf[3] = '\0';
     colorprint(r+6, k*4+6, cur -> kind , buf );

}


unsigned int dispmat() {

    int i,j,r,k,ry,n;
    struct m_type * ma = NULL;
    char c, buf[83];

/*
struct m_type {

     unsigned int naam;       / * voor testen routines                * /
     char ligature[3];        / * room for 3 chars: ffi, ffl max...   * /
     unsigned char kind;      / * roman, italic, small cap, bold      * /
     unsigned char width;     / * nominal witdh in units              * /
     unsigned char row;       / * row in matrix                       * /
     unsigned char col;       / * colom in matrix                     * /
			      / * 0-16, 17=> outside matrix !         * /
     unsigned long int code;  / * the actual code                     * /
     unsigned char u[2];      / * uitvulling / wedges-positions       * /

     struct m_type *_fore;    / * verwijzen            * /
     struct m_type *_next;    / * verwijzen in de ring * /
} ;
*/
    cls();
    strcpy(buf,centerrec.charname);
    colorprint(2,5,0,buf);
    strcpy(buf," series:");
    colorprint(2,21,0,buf);
    strcpy(buf,centerrec.nummers);
    colorprint(2,40,0,buf);
    sprintf(buf," set %6.2f ",( (float) centerrec.set)*.25 );
    colorprint(2,50,0,buf);
    strcpy(buf," ");
    colorprint(4,5,0,buf);
    for (k=0;k<=16;k++) {
       for (i=0;i<3;i++) buf[i]= ncols[k][i]; buf[3]=' ';
       buf[4]='\0';
       colorprint(4,k*4+6,0,buf);
    }
    for (i=0;i<15;i++) {
	sprintf(buf,"%2d",i+1);
	colorprint(i+6,2,0,buf);
	sprintf(buf,"%2d",centerrec.cwedge[i]);
	colorprint(i+6,74,0,buf);
    }
    k=0; r=0;
    for (ma = matrix ; ma != NULL; ma = ma -> _next){
	r = ma -> row;
	k = ma -> col;
	if (k<=16) {
	   dispma( ma );
	   /*
	   for (i=0;i<3;i++) buf[i]= ma -> ligature[i] ; buf[3] = '\0';
	   colorprint(r+6, k*4+6, ma -> kind , buf );
	   */
	}
    }
}

void dispbuiten() /* display buitenmatrijzen */
{
    int i,j,r,k,ry,n=0;
    struct m_type * ma = NULL;
    char c, buf[80],buff[83];
    struct rccoord opos;

    _displaycursor(_GCURSORON);
    do {
	sprintf(buf," buitenmatrijzen in rij ");
	colorprint(24,0,0,buf);
	/* l2_int */
	opos = _gettextposition();
	ry = l2_int(0, MAXRIJ+1,opos.row,opos.col);
  sprintf(buf,"                                                           ");
	for (i=21;i<=24;i++) colorprint(i,1,0,buf);

	if ( (ry>0) && (ry<=MAXRIJ + 1 ) ) {
	   ry1.p = NULL;
	   disp_buit( ry );

	   if (ry1.p != NULL) {
	       sprintf(buf,"                                                           ");
	       colorprint(23,1,0,buf);
	       sprintf(buf,"aantal %2d m =",ry1.n);
	       colorprint(23,1,0,buf);
	       for (i=0;i<2;i++) buf[i] = ry1.p -> ligature[i]; buf[3]='\0';
	       colorprint(23,16, ry1.p -> kind, buf);
	   } else {
	       sprintf(buf,"aantal buiten =%2d ",ry1.n);
	       colorprint(23,1,0,buf);
	   }
	}
     }  while (ry > 0);
}

unsigned int _defa_ult_matrix()
{
   int i,j,l,n,r,k,aantal =0;
   struct m_type * cur, *pp;
   char buf[83];

   cls();
   strcpy(buf,"default matrix \n");
   pos = _gettextposition();
   colorprint(pos.row,pos.col,0,buf);
   pos = _gettextposition();
   cursorpos(pos.row, pos.col, INVOEGEN, AAN );

   getchar();

   data_copy( &centerrec , &garamond );

   wissen_matrix(); /* als matrix gevuld is: wissen oude matrix */
   for ( cur = &garamnd12[0] ; cur !=NULL; cur = cur -> _next) {
       /* dit in een aparte routine
	   kan gebruikt worden bij lezen vanuit file

       */
       pp = vrijmaken();
       copypp(pp,cur);
       if (matrix == NULL) {
	   matrix = pp;
	   eindmatrix = matrix;
       } else {
	   eindmatrix = achtervoegen(pp,eindmatrix);
       }
       /* werk bezet-array bij */
       r = cur -> row;
       k = cur -> col;
       bezet[r][k] = 1;
       n = strlen(cur->ligature);
       if ( n > 1) {
	   if (n == 1) {
	       verwijs[(cur -> kind)][ (cur -> ligature[0])] = pp;
	   } else {
	       pp = vrijmaken();
	       copypp(pp,cur);
	       if ( ligaturen == NULL) {
		   ligaturen = pp ;
		   endligtrn = pp ;
	       } else {
		   endligtrn = achtervoegen( pp , endligtrn );
	       }
	   }
       }
       /* ligaturen zoeken */
       /* verwijstabel maken */
       aantal++;
   }
   return(aantal);
}

unsigned int _new_matrix( ){
    /* cls() */

    int n,i,j,k,c, iantw, min = 5 , max = 18,rij, kolom,antw;
    float fl;  double dbl;
    int mat_aant = 0;
    struct m_type *pp;
    unsigned long int cc, claatste;
    unsigned int wig, cset;
    char buf[20];   /* voor lezen */
    char buff[83]; /* voor schrijven */

    unsigned char uu[2];
    struct rccoord opos;
    long recseek;
    size_t recsize = sizeof( struct m_type );

    wissen_matrix();
    clsblauw();

    sprintf(buff," routine: _new_matrix ");     colorprint(1,1,0,buff);
    sprintf(buff," nieuw matrix inlezen  ");    colorprint(2,1,0,buff);
    sprintf(buff," o_central aanroepen:  ");    colorprint(3,1,0,buff);
    sprintf(buff,"   om filenaam maken + matrixfile te openen\n");
						colorprint(4,1,0,buff);
    sprintf(buff," in deze routine:      ");    colorprint(5,1,0,buff);
    sprintf(buff,"    matrix inlezen     ");    colorprint(6,1,0,buff);
    sprintf(buff,"    matrix wegschrijven ");   colorprint(7,1,0,buff);
    sprintf(buff,"    file sluiten        ");   colorprint(8,1,0,buff);
    sprintf(buff," aanroepen: verwystab() ");   colorprint(9,1,0,buff);
    sprintf(buff,"    verwijstabellen maken "); colorprint(10,1,0,buff);
    getchar();

/* struct data_matrix {
     char charname[40];       / * naam letter              * /
     char nummers[15];        / * monotype aanduidingen    * /
     unsigned int  set;       / * width largest character in pica-points * 4 * /
     unsigned int  corps[2];  / * corps engels / didot in 1/2 punten * /
     char charwedge[8];       / * monotype aanduiding wig  * /
     unsigned int cwedge[16]; / * indeling wig * /
	    / * a:\\mat00001.mat"
		d:\\monotype\\mat00001.mat"
		12 456789012 45678901234
	    * /
     char filenaam[30];       / * filenaam van matrix-file * /
     unsigned int aantal;     / * aantal letters totaal * /
} centerrec ;
*/
     cls();

     sprintf(buff,"naam letter     : ");
     colorprint(3,1,0,buff);
     n = get_line(centerrec.charname,40);
	/* for (i=0;i<n;i++) centerrec.charname[i]=regelbuff[i]; */
     sprintf(buff,"monotypenummers : ");
     colorprint(4,1,0,buff);
     n = get_line(centerrec.nummers,15);
	/*for (i=0;i<n;i++) centerrec.nummers[i]=regelbuff[i]; */
     /* _settextposition(5,1); */
     centerrec.set = inlezen_set(5,1);

     cset = centerrec.set;
     sprintf(buff,"corps in pica's engels : ");
     colorprint(6,1,0,buff);
     opos = _gettextposition();
     fl = l2_real(5.0, 24.0,opos.row,opos.col) + 0.25 ; fl *= 2;
     c = fl ;
     centerrec.corps[0] = c;

     sprintf(buff,"corps in punten didot  : ");
     colorprint(7,1,0,buff);
     opos = _gettextposition();
     fl = ( l2_real(5.0, 24.0,opos.row,opos.col) + 0.25) * 2.0;
			/* afronden op .5 */
     centerrec.corps[1] = (int) fl;
     sprintf(buff,"corps %3d ",centerrec.corps[1]);
     colorprint(7,50,0,buff);
     sprintf(buff,"corps %5.1f ", fl *0.5 );
     colorprint(7,65,0,buff);
     getchar();
     for (i=0;i<=14;i++){
	sprintf(buff," rij %2d : unit-dikte letterwig = ",i+1);
	colorprint(8,1,0,buff);
	opos = _gettextposition();
	c = l2_int( min, max,opos.row,opos.col);
	centerrec.cwedge[i] = c;
	min = c;
     }
     sprintf(buff,"monotype-aanduiding wig :");
     colorprint(9,1,0,buff);
     n = get_line(centerrec.charwedge,8);

     /* central file aanroepen */

     o_central( 'n' );

     /* for (i=0;i<n;i++)centerrec.charwedge[i]=regelbuff[i]; */
     /* aantal tellen ...... */
     /* start rij matrices   */
     cls();
     for (rij = 0;rij<=14;rij++) {

	wig = centerrec.cwedge[rij];

	for (kolom = 0; kolom <=16; kolom ++) {
	    cc = rcodes[rij] ;
	    cc = cc | kcodes[kolom];


	    sprintf(buff,"inhoud matrijs rij %2d kolom %2d ",rij+1,kolom+1);
	    colorprint(2,1,0,buff);
	    n=get_line(buf,3);    /* lees string in */
	    if (n > 0 ) { /* if lengte > 0 is er een karakter */
		pp = vrijmaken();
		pp -> row = rij;
		pp -> col = kolom;
		/* lees_matrijs( pp, buf); */
		/* inlezen matrijs */
		for (i=0;i < n;i++){ pp -> ligature[i]=buf[i]; }
		sprintf(buff," soort \? romein = 0, italic = 1 klein kap = 3, vet = 4");
		colorprint(3,1,0,buff);
		opos = _gettextposition();
		pp -> kind = l2_int(0,4,opos.row,opos.col);
		pp -> row = rij ;
		pp -> col = kolom ;
		uu[0]=3; uu[1]=8;
		sprintf(buff,"dikte letter ");
		colorprint(4,1,0,buff);
		opos = _gettextposition();
		iantw = l2_int(0,23,opos.row,opos.col);
		if ( ! iantw ) iantw = wig ;
		if (iantw != wig ) {
		    ber_u1u2(cset, wig, iantw - wig );
		    uu[0] = uitvul[0] ;  uu[1] = uitvul[1];
		    cc |=  _Snaald;
		} else {
		    uu[0] = 3; uu[1] = 8;
		    claatste = cc ;
		}
		pp -> code = cc;
		pp -> u[0] = uu[0];
		pp -> u[1] = uu[1];

		if ( ! mat_aant ) {
		   matrix = pp  ;
		   eindmatrix = matrix;
		} else {
		   eindmatrix = achtervoegen( pp, eindmatrix);
		}

		if (n == 1) {
		   verwijs[(pp -> kind)][ (pp -> ligature[0])] = pp;
		} else {
		   if ( ligaturen == NULL) {
		       ligaturen = pp ;
		       endligtrn = pp ;
		   } else {
		       endligtrn = achtervoegen( pp , endligtrn );
		   }
		}

		fseek(matrixfl, 0L,SEEK_END );
		fwrite( pp, recsize,1,matrixfl);
		centerrec.aantal ++;
		mat_aant ++;
	    }
	}
	cls();
	sprintf(buff," hoeveel buiten matrijzen op rij %4d ",rij);
	colorprint(2,1,0,buff);
	opos = _gettextposition();
	n = l2_int(0,20,opos.row,opos.col);
	if (n>0) {
	   cc = claatste;
	   for (i=1;i<=n;i++) {
	       do {
		 sprintf(buff,"inhoud matrijs : %2d ",17+i);
		 colorprint(3,1,0,buff);
		 n=get_line(buf,3);    /* lees string in */
	       } while ( ! n );
	       if (n > 0 ) { /* if lengte > 0 is er een karakter */
		  pp = vrijmaken();
		  for (i=0;i < n;i++){ pp -> ligature[i]=buf[i]; }
		  sprintf(buff," soort \? romein = 0, italic = 1 klein kap = 3, vet = 4");
		  colorprint(4,1,0,buff);
		  opos = _gettextposition();
		  pp -> kind = l2_int(0,4,opos.row,opos.col);
		  pp -> row = rij ;
		  pp -> col = kolom ;
		  uu[0]=3; uu[1]=8;
		  sprintf(buff,"dikte letter ");
		  colorprint(5,1,0,buff);
		  opos = _gettextposition();
		  iantw = l2_int(0,23,opos.row,opos.col);
		  if ( ! iantw ) iantw = wig ;

		  if (iantw != wig ) {
		     /* uitvulling berekenen */
		     ber_u1u2(cset, wig , iantw - wig );
		     uu[0] = uitvul[0] ;  uu[1] = uitvul[1];
		     cc |= _Snaald;
		  } else {
		     uu[0] = 3; uu[1] = 8;
		  }
		  pp -> code = cc;
		  pp -> u[0] = uu[0];
		  pp -> u[1] = uu[1];
		  if ( ! mat_aant ) { /* eerste record ! */
		     matrix = pp  ;
		     eindmatrix = matrix;
		  } else {
		     /* achtervoegen */
		     eindmatrix = achtervoegen( pp, eindmatrix);
		  }
		  if (n == 1) {
		     verwijs[(pp -> kind)][ (pp -> ligature[0])] = pp;
		  } else {
		     /* ligatuur */
		     if ( ligaturen == NULL) {
			ligaturen = pp ;
			endligtrn = pp ;
		     } else {
			endligtrn = achtervoegen( pp , endligtrn );
		     }
		  }
		  fseek(matrixfl, 0L,SEEK_END );
		  fwrite( pp, recsize,1,matrixfl);
		  centerrec.aantal ++;
		  mat_aant ++;
	       }
	   }
	}
     }

   /* verwijstabellen maken */
   fclose(matrixfl);
   /* cset gebruikt ??? */
   return (mat_aant);
}

float l2_real(float min, float max,int r, int k)
{
    float terug;
    int n=0;
    char buf[60];

    do {
	n++;
	sprintf(regelbuff," voer een getal in: ");
	colorprint(r,k,0,regelbuff);

	tooncur(INVOEGEN, buf, 15);

	/* cgets( regelbuff ); cputs( "\n\r" );*/

	terug =  atof( buf ) ;
	sprintf(regelbuff,"gelezen %10.4f ",terug);
	colorprint((r+1),k,0,regelbuff);

	getchar();

	if ((terug<min) || (terug>max)) {
	    sprintf(regelbuff," min = %10.4f max = %10.4f ingelezen: %10.4f ",
				min,max,terug);

	    colorprint(r+1,k,0,regelbuff);
	    tooncur(INVOEGEN, buf, 2 );
	}
	if (n>10) goto br;
   } while ((terug < min) || (terug > max));
   br:
   return(terug);
}

int l2_int(int min, int max,int r, int k)
{
    int terug,r1,n,i ;
    char buf[80],c;

    do {
	sprintf(buf,"           ");
	colorprint(r,k,0,buf);
	sprintf(buf," :");
	do {
	   colorprint(r,k,0,buf);
	   n = tooncur(UNDERLINE, regelbuff, 10 );
	   /*
	      sprintf(buf," n = %3d ",n);
	      colorprint(r+1,1,0,regelbuff);
	      for (i=-1;i<3;i++) {
		sprintf(buf," w[%2d] = %3d ",i,regelbuff[i]);
		colorprint(r+i+4,1,0,buf);
		getchar();
	      }
	      c=getchar();
	      if (c=='#') break;
	   */
	} while ( regelbuff[0]==10 );
	terug =  atoi( regelbuff ) ;
	if ((terug<min) || (terug>max)) {
	    sprintf(buf," min = %10d max = %10d ingelezen: %10d \?        ",
				min,max,terug);
	    r1 = (r<23) ? r+1 : r;
	    colorprint(r1,k,0,buf);
	    tooncur(UNDERLINE, regelbuff, 1 );
	}
   } while ((terug < min) || (terug > max));
   return(terug);
}

/* ************************************************************** *
 *     ber_u1u2                                                   *
 *              berekenen plaats uitvulwiggen bij toevoegen       *
 *     van letterbreedte aan de gegoten letter                    *
 *     letter aan/afspatieren of letter op 'verkeerde plaats'     *
 *     in de matrix                                               *
 *                                                                *
 *         input: set als int: 4* de reeele waarde                *
 *                dikte letter = in units                         *
		  toetevoegen dikte in units monotype
	   rekening houden met de minimale dikte van de letter

	   globals: uitvul[0] = u1;  uitvul[1]=u2;

	   min: 4 eenheden

 * ************************************************************** */

void ber_u1u2(unsigned int set, unsigned int ldikte, int toevoeg)

{

    float ss,ub,b,v;
    unsigned int u, u1, u2, ld;
    int    afr, toevoeg2;
    float dikte1, d;

    toevoeg2 = toevoeg;
    ld = ldikte + toevoeg2;
    if (ld < 4 ){
	toevoeg2 += (4 - ld) ;
    } /* minder dan 4 eenheden wordt er niet gegoten */

    ss = set * 0.25 ;
    ub = ss  * 7.716;

    /* printf(" set = %5.2f ",ss); */

    dikte1 = ss * 7.716 * ldikte ;  /* dikte letter */

    /* printf("d1= %8.3f ",dikte1); */


    u1=0; u2=0;

    b = toevoeg2 * ub;    /* + 2.5 ; b /= 5; */
    /* printf("b= %7.2f ",b); */
    if (b<0) {
       afr = ((b-2.5)/5);
    } else {
       afr = ((b+2.5)/5);
    }

    /* printf("afr= %4d",afr); */

    if ( (afr >=-37) && (afr < 187 ) ){

	/* de grensen van afhalen of toevoegen */

	d = dikte1 + (afr*5.0) ;
	/* printf("binnen de grensen d = %7.2f \n",d); */
	/* zo dik zou de letter kunnen worden */
	/* maar dat mag niet teveel worden ! */

	if (set<48  ) { /* bij set <12 : max dikte letter = 0.1560" */
		  v = 1560.0 - d ;
	}
	else {          /* bij set >= 12  : max dikte = 0.1660" */
		  v = 1660.0 - d ;
	}
	/* printf(" v = %7.2f \n",v); */
	if (v>=0) {
	    u = 53 + afr;
	    u1 = u / 15; u2 = u % 15;
	    if (u2 == 0) {
		u1--; u2 += 15;
	    }
	    /* printf(" uitvulling %3d / %2d \n",u1,u2); */
	}
    }
      /* printf(" in de else-lus "); */

    uitvul[0]=u1;  uitvul[1]=u2;   /* globals ! */
}

int filesopenen()
{
    /* FILE *infile, *outfile; */

    char inpath[_MAX_PATH], outpath[_MAX_PATH];
    char drive[_MAX_DRIVE], dir[_MAX_DIR];
    char fname[_MAX_FNAME], ext[_MAX_EXT];
    int  in, size;
    long i = 0L;

    /* Query for and open input file. */
    do {
	printf(" probeer: d:\\monotype\\testfile.txt\n");
	printf(" Enter input file name: " );
	gets( inpath );
	strcpy( outpath, inpath );
	if( (infile = fopen( inpath, "rb" )) == NULL )
	{
	    printf( "Can't open input file" );
	   /* return( 1 ); niet onderbreken */
	}
    } while (infile == NULL); /* ik wil met een file komen */

    /* Build output file by splitting path and rebuilding with
     * new extension.
     */
    _splitpath( outpath, drive, dir, fname, ext );
    strcpy( ext, "mon" );
    _makepath( outpath, drive, dir, fname, ext );

    /* If file does not exist, open it */
    if( access( outpath, 0 ) )
    {
	outfile = fopen( outpath, "wb" );
	printf( "Creating %s from %s . . .\n", outpath, inpath );
    }
    else
    {
	outfile = fopen(outpath,"r+"); /* voor schrijven en lezen */
	printf( "Output file already existed" );
	/* exit( 1 );                          */
    }
    return(0);
}

int filesluiten()  /* sluit invoer en uitvoer */
{
    fclose( infile );
    fclose( outfile );
    return(1);
}

unsigned lezen()
{
    char  /* int */ in, size;
    long i = 0L;
    unsigned int aantalletter, plaats_cursor;
    char *buff1, *buff2;

    printf( "(B)yte or (W)ord: " );
    size = getche();
    _clearscreen( _GCLEARSCREEN ); /* cls(); */

    /* Get each character from input and write to output. */

    aantalletter = 0;
    while( 1 )
    {
	    /* This example uses the fgetc and fputc functions. You
	     * could also use the macro versions:
	    in = getc( infile );
	     */
	    in = fgetc( infile );
	 /*   opslag[aantalletter]=in;*/
	    if (aantalletter<60) {

	    } else {

	    }

	    /* hier is de controle van de lus */
	    if( (in == EOF) && (feof( infile ) || ferror( infile )) )
		break;


	    /* fprintf( outfile, " %.2X", in ); */
	    printf("%2c %3d ",in,in);
	    getchar();
	    if( !(++i % 16) )
	    {
		/* Macro version:
		putc( 13, outfile );
		 */
		fputc( 13, outfile );           /* New line      */
		fputc( 10, outfile );

		printf("\n");
		getchar();
	    }

    }
}

unsigned char inlezen_set(int r,int k)
{
	float rset;
	char buf[83];
	unsigned char s;
	struct rccoord opos;

	sprintf(buf,"geef de set ");
	colorprint(r,k,0,buf);

	opos = _gettextposition();
	rset = l2_real( 5.0 , 26.0,opos.row,opos.col) + .125;
			/* rset += .125; afronden op kwarten */
	rset *= 4;      /* set is aantal pica-punten in kwarten */
	s = rset;       /* alleen de helen */
	return(s);
}

void data_copy(struct data_matrix *dest, const struct data_matrix *source)
{
   int l,i,j;
   l=strlen(source->charname);
   for (i=0;i<l;i++) dest -> charname[i] = source -> charname[i];
   l=strlen(source->nummers);
   for(i=0;i<l;i++) dest -> nummers[i] = source -> nummers[i];
   dest -> set = source -> set;
   dest -> corps[0] = source -> corps[0];
   dest -> corps[1] = source -> corps[1];
   l=strlen(source -> charwedge);
   for(i=0;i<l;i++)  dest -> charwedge[i] = source -> charwedge[i];
   for(i=0;i<16;i++) dest -> cwedge[i] = source -> cwedge[i];
   l=strlen(source -> filenaam);
   for(i=0;i<l;i++)  dest -> filenaam[i] = source -> filenaam[i];
   dest -> aantal = source -> aantal;
}

/***************************************************************/
/*   functions to control the pointer-arithmatic of the editor */
/***************************************************************/

/****************************************************************/
/*  gereed maken opslag                                         */
/*                                                              */
/*                                                              */
/****************************************************************/

void gereedmaken_opslag( void ) /* gereedmaken double ring-structure */
{                               /* refering to each other structure */
     int i;

     opslag[0].naam = 0;
     clear_record( & opslag[0]);

     opslag[0]._fore = & opslag[0];
     opslag[0]._next = & opslag[0];
     for ( i = 1; i <= MAXOPSLAG -1; i++ )
     {
	  opslag[i].naam = i;
	  clear_record( & opslag[i] );
	  opslag[i-1]._next = & opslag[i];
	  opslag[i]._fore = & opslag[i-1];
     }
     opslag[MAXOPSLAG-1]._next = & opslag[0];
     opslag[0]._fore = & opslag[MAXOPSLAG-1];
     opslag[0]._next = & opslag[1];
     printf("einde gereedmaken ");
     getchar();
}

/****************************************************************/
/*  vrijmaken  get record from the storage                      */
/*                                                              */
/*                                                              */
/****************************************************************/

struct m_type * vrijmaken(void)         /* get record from storage */
{
     struct m_type *px;

     px = opslag[0] . _next;                 /* this record will be used */
     opslag[0] . _next = px -> _next;        /* adres next unused record */
     (px -> _next) -> _fore = & opslag[0];   /* the root */
     px -> _fore = NULL;                    /* this has to be set first */

     return px;
}

void clear_record(struct m_type *p)
{
     int j;

     for (j=0; j<=3; j++) p -> ligature[j] = '\0';
     p -> ligature[3]='\0';
     p -> kind  =  0;
     p -> width =  0;  /* nominal witdh in units      */
     p -> row   = 16;  /* row in matrix               */
     p -> col   = 18;  /* colom in matrix             */
		       /* 0-16, 17=> outside matrix ! */
     p -> u[0]  =  0;  /* uitvulling u1/u2            */
     p -> u[1]  =  0;  /*                             */
     p -> code  =  0;
     p -> _fore = NULL;
     p -> _next = NULL;

}

/****************************************************************/
/*    terugzetten : puts a record back in the storage           */
/*       direct after the root                                  */
/*    first version: 20 jan last version: 3 feb                 */
/****************************************************************/

void terugzetten(struct m_type *px)   /* put record in storage */
{
     /*char c;*/

     printf(" terugzetten : %3d ", px -> naam );
     getchar();

     px -> _next = opslag[0]._next; /* after the first element        */
     px -> _fore = & opslag[0];     /* px points to the root          */
     (px -> _next) -> _fore = px;   /* reference in both directions   */
     opslag[0]._next = px;          /* de root point to its successor */
     px -> ligature[0]='\0';        /* clear all values !!!!          */

     printf(" %3d <- record[0] wijst -> %3d \n", (opslag[0]._fore)->naam,
	  (opslag[0]._next)->naam );
     printf(" %3d <- px %3d wijst -> %3d \n", (px -> _fore)->naam,
	  px->naam, (px -> _next)->naam );


     getchar();
}

/****************************************************************/
/*   showvoorraad: shows the unused storage of pointer-records  */
/*   first version: 2 feb, last: 2 feb 2001                     */
/****************************************************************/

void show_voorraad(unsigned int start, unsigned int aantal, int r)
{
   unsigned int i,j=0;
   struct m_type *p;
   char c;

   if ( r>0)
     printf("heen  door de voorraad \n");
   else
     printf("terug door de voorraad \n");

   p = & opslag[start];
   for (i = 0; i<aantal; i++){
      if (r>0)
       printf("%3d->%3d ",p->naam, (p->_next)->naam);
      else
       printf("%3d->%3d ",p->naam, (p->_fore)->naam);

      p = (r > 0) ? p -> _next : p -> _fore;

      if ((j % 10)==0){
      c = getchar();
      }
      j++;
      if (c == '#') return;
   }
}

/****************************************************************/
/*   start_rij: starts the line, takes the first record away    */
/*     from the storage                                         */
/*   first: 29 jan, last 2 feb 2001

     deze functie is heel algemeen:
	   hij haalt een record uit de voorraad, en geeft de
	   pointer ernaar terug
     kan gebruikt worden voor de reeks records waarin de matrix
     zit, en voor de reeks records waarin de ligaturen zitten

*/
/****************************************************************/

struct m_type * start_rij( char c[] )
		/* wens: een ligatuur direkt in het record stoppen */
{
     struct m_type * cursor;

     printf("start_rij met letter %3c ",c[0] );
     cursor = vrijmaken();     /*  haal record uit voorraad */
     cursor -> ligature[0]=c[0] ;  /*  fill record */
	       /* in de lettertabel kijken                */
	       /* string erin stoppen                     */
	       /* row, col, width, code, berekenen        */
     return cursor;
}

/****************************************************************/
/*   achtervoegen                                               */
/*                                                              */
/*                                                              */
/****************************************************************/

struct m_type * achtervoegen(struct m_type *px, struct m_type *einde)
{

     /* printf("achtervoegen"); getchar(); */

     einde -> _next = px;   /* this will be the end of the edit-line   */
     px -> _next = NULL;    /* points to nothing                       */
     px -> _fore = einde;   /*                                         */
     einde = px;

     return px;             /*  new "einde" */
}

/****************************************************************/
/*  in de rij, puts a record in the line, after the position    */
/*      of the cursor, = next position of the cursor            */
/*                                                              */
/****************************************************************/

void in_de_rij(struct m_type *cursor, struct m_type *px)
{
     printf("na %3d n de rij voegen van record %3d ",
		    cursor->naam,px->naam );

     px -> _next = cursor -> _next;  /*  px->_next points to the next */
				     /*            record             */
     px -> _fore = cursor ;          /*  px->_fore points the other   */
				     /*          direction            */
     (px -> _next) -> _fore = px;    /*  the successor of px          */
				     /*  should point to px           */
     cursor -> _next = px;           /*  the cursor point to px       */
     cursor = px;                    /*  de cursor verzetten          */

  /*   teruggeven van de pointer cursor Qc laat een routine niet toe
	  de pointer aan te passen */

}

/****************************************************************/
/*    del = delete record direct next to the cursor             */
/*    first version: 15 jan   last: 2 feb 2001                  */
/****************************************************************/

struct m_type * del ( struct m_type *cursor )
	  /* delete record after the cursor  */
{
    struct m_type *cur;
    struct m_type *px;
    struct m_type *p1;

    cur = cursor;

    printf("delete record na %3d ",cur -> naam);

    if (cur -> _next != NULL){ /* then there's something to get rid off*/
       px = cur -> _next;
       p1 = px -> _next;
       if (p1 != NULL) {
	  p1  -> _fore = cur;   /* refere to each other*/
	  cur -> _next = p1;
       } else { /* the end of the line*/
	  cur -> _next = NULL;
       }
       px  -> _next = NULL;  /* blank pointers            */
       px  -> _fore = NULL;
       terugzetten (px);     /* put it back in the storage */
    }
    return cur; /* the correct way to return cursor to the program */
}

/****************************************************************/
/*    backsp : deletes the record the cursor points to          */
/*                                                              */
/*    first: 29 jan, last: 2 feb                                */
/****************************************************************/

struct m_type * backsp( struct m_type *cursor)
{
     struct m_type *px;
     struct m_type *p1;
     struct m_type *cur;

     printf("delete record %3d ", cursor -> naam);
     getchar();

     cur = cursor;
     px = cur -> _next;
     if (cur == begin_regel) {
	 printf("cursor op begin_regel ");
	 getchar();
	 begin_regel = inkorten ( cur );
	 return;
     }
     if ( px != NULL ) {         /* there's a record after the cursor*/
	 p1 = cur -> _fore;
	 if (p1 != NULL) {       /* there's a record before the cursor*/
	  p1 -> _next = px;      /* refere to each other: */
	  px -> _fore = p1;
	  cur -> _next = NULL;
	  cur -> _fore  = NULL;
	  terugzetten(cur);
	  cur = px;
	 } else {               /* there's no record before the cursor */
	  px -> _fore  = NULL;
	  cur -> _next = NULL;
	  cur -> _fore = NULL;
	  terugzetten(cur);
	  cur = px;
	 }
     } else {                  /* there's NO record after the cursor  */
	 p1 = cur -> _fore;
	 if (p1 != NULL) {
	       /* there's at least one more record before the cursor */
	    p1 -> _next = NULL;
	    cur -> _fore = NULL;
	    terugzetten(cur);
	    cur = p1;
	    einde_regel = cur;
	 } else { /* there's also NO record before the cursor        */
	    terugzetten(cur);
	    cur = NULL;
	    begin_regel = NULL;
	    einde_regel = NULL;
	 }
     }
     return cur;
}

/****************************************************************/
/*   inkorten : shortens the line with one record, from the     */
/*      root of the line, the record is storage again           */
/*   first version: jan 15, last :  2 feb 2001                  */
/****************************************************************/

struct m_type * inkorten( struct m_type *strt )
{
    struct m_type *p1;

    p1 = strt;                 /* preserve pointer-value*/
    if ((strt -> _next) != NULL) {
       strt = strt -> _next;     /* set new value strt         */
       strt -> _fore = NULL;     /* no records before this one */
       printf(" begin record : %3d -> %3d \n",strt->naam, strt -> _next );
       printf(" terug record : %3d \n",p1->naam);
       getchar();
       p1->_next = NULL;
       terugzetten(p1);    /* put record in storage*/
    } else {
       terugzetten(p1);  /* put record in storage  */
       strt = NULL;        /* no more records in the line */
    }
    return strt;
}

/****************************************************************/
/*    show_rij: shows the content of the line                   */
/*    first version: 2 feb   last version: 2 feb 2001           */
/****************************************************************/

void show_rij( struct m_type *cur , int direct )
{
    struct m_type * crsr;

    char c;
    int j=0;

    crsr = cur;
    if (crsr == NULL) {
       printf("start-pointer has value: NULL in routine show_rij ");
       getchar();
       return;
    }
    printf("cur -> naam %3d ",crsr->naam);
    if (direct<0) {
       printf("terug door de rij: \n");
    } else {
       printf("heen  door de rij: \n");
    }
    do {
       c = crsr -> ligature[0];
       switch (c) {
	  case 10 : printf("LF "); break;
	  case 11 : printf("VT "); break;
	  case 12 : printf("FF "); break;
	  case 13 : printf("CR "); break;
	  default : printf("%2c ",c);
       }
       /* printf("%2c ",  crsr -> ligature[0] ); */
       crsr = (direct<0) ? crsr -> _fore : crsr -> _next;
       j++;
    } while (crsr != NULL) ;
    printf("\n");
    crsr = cur;
    j = 0;
    do {
       printf("%2d ",  crsr -> naam );
       crsr = (direct<0) ? crsr -> _fore : crsr -> _next;
       j++;
    } while (crsr != NULL) ;
    getchar();
}

struct m_type  * voeg_toe( char *c, struct m_type * cursor )
{
     struct m_type *px;
     int i;

     printf("voeg toe ");

     px = vrijmaken();
     for(i=0; c[i] != '\0' && i<3 ; i++)
	 px -> ligature[i] = c[i];

     return achtervoegen( px, cursor ) ;

}


unsigned get_line2(int r, int k, char *s , unsigned lim)
{
    int c,i;

    _settextposition(r,k);
    _displaycursor(_GCURSORON);

    for (i=0;i<lim-1 && (c=getchar())!=EOF && c!='\n';i++){
       s[i]=c;
    }
    if (c=='\n') { s[i]=c; i++; } s[i]='\0';
    return (i);
}


unsigned get_line(char *s , unsigned lim)
{
    int c,i;

    _displaycursor(_GCURSORON);

    for (i=0;i<lim-1 && (c=getchar())!=EOF && c!='\n';i++){
       s[i]=c;
    }
    if (c=='\n') { s[i]=c; i++; } s[i]='\0';
    return (i);
}

void split_str(char *b, char *l, char *r, unsigned int k)
{
   unsigned int i,j;

   for (i=0;i<k;i++) l[i]=b[i];
   l[i]='\0';
   j=0;
   while (b[i] != '\0'){
      r[j++] = b[i++];
   }
   r[j]='\0';
}




int main3( void )
{
    short blink, fgd, oldfgd;
    long bgd, oldbgd;
    struct rccoord oldpos;
    char buffer[83];
    char c,buf[30];
    int i,j,k,n;
    float f;

    int cc,cc1,cc2;
    char c1,c2;

    clsblauw();
    /*
    do {
       cc = getchar();
       cc1 = cc & 0x0f;
       cc1 >>= 8;
       cc2 = cc &0xf0;
       c1=cc1; c2 = cc2;
       printf(" cc1 = %3d cc2 = %3d ",c1,c2);
       getchar();

    } while (cc != '#');
    if (cc == '#') exit;
    */
    /* Save original foreground, background, and text position. */
    oldfgd = _gettextcolor();
    oldbgd = _getbkcolor();
    oldpos = _gettextposition();


     _displaycursor(_GCURSORON);
     clsblauw();

     /* getchar();*/
     /*
     for (i=0;i<20;i++) {
	sprintf(buffer," nummer gelezen %2d ",
		 vraagkolom( 10, 10 ) );
	colorprint(10,20,0,buffer);
	getchar();
     }
     */
     /*
     f = l2_int(-1,25,1,1);
     sprintf(buffer,"ingelezen : %8.5f ",f);
     _settextposition(10,10);
     pos = _gettextposition();
     colorprint(pos.row,pos.col,0,buffer);
     getchar();
     */
     /*
     sprintf(buffer,"nu full block");
     colorprint(pos.row+1,1,0,buffer);
     tooncur(FULLBLOCK, buf, 2 );

     sprintf(buffer,"nu underline");
     colorprint(pos.row+2,1,0,buffer);
     tooncur(UNDERLINE, buf, 2 );

     sprintf(buffer,"nu double underline");
     colorprint(pos.row+3,1,0,buffer);
     tooncur(DOUBLEUNDERLINE, buf, 2 );
     */

     /* textmain();*/
     /* printf("Besta ik of besta ik niet \?\n");*/
     /* getchar();*/
     /* j = genereer(3824, buf);
	printf(" gemaakt lengte =%4d :",j);
	for(i=0;i<j;i++)printf("%1c",buf[i]);
	getchar();
	*/

     gereedmaken_opslag(); /* gereedmaken records */
     n = _defa_ult_matrix();
     printf(" totaal %4d records", n);
     getchar();
     /* for (k=0,i=0,j=0;k<80;k++) {
	 sprintf(buf,"%1d",k%10);
	 print_at(1, k, buf);
     }  */
     dispmat();    /* display actueel matrijzenraam */
     dispbuiten(); /* display buitenmatrijzen */

     cls();
     /*
     for(i=0;i<80;i++)buf[i]=' '; buf[80]='\0';
     for(i=0;i<=25;i++) colorprint(i,1,0,buf);
     */

     _change_matrix();
     printf("we gaan er nu uit ");
     getchar();
     _settextcursor( DOUBLEUNDERLINE );
     goto einde;


     /* verwijs tabel wissen */
     for (i=0;i<=3;i++) {
	for (j=0;j<=255;j++) verwijs[i][j]=NULL;
     }
     /* ligaturen verwijstabel */
     hoofdmenu();

     /* main2(); */

     /* maintest(); */

     c=getchar();

     if (c=='#') return 1;     else return 0;

    einde:

    /* Restore original foreground and background. */
    _settextcolor( oldfgd );
    _setbkcolor( oldbgd );
    _clearscreen( _GCLEARSCREEN );
    _settextposition( oldpos.row, oldpos.col );

}

/* display contents of a number of records and wait for a key to hit */
void weergeven(struct m_type *p, int n, int r, int k)
{
    int i;
    char buf[85];
    struct m_type * cur;

    cur = p;
    for (i=0;i<n;i++){
       if (cur != NULL) {
	  sprintf(buf,"i %2d l = %1c r %2d k %2d d %2d       ",
		    i,cur->ligature[0],cur -> row, cur -> col, cur -> width);
	  aandacht(r,k,buf);
	  cur = cur -> _next;
       }
    }
}




main()
{
    printf("Main ");

    getchar();
    printf("Nu naar main 3");
    getchar();
    cls();
    main3();
    clsblauw();
}

char aandacht(int r,int k, char buf[])
{
    colorprint(r,k,0,buf);
    _settextcursor( DOUBLEUNDERLINE );
    _displaycursor( _GCURSORON );
    return(getchar());
}

unsigned int _change_matrix(){ /* veranderen van al bestaande matrix */

   int doorgaan = 1, leeg, found, _bezet;
   int r,k,v1,v2,ver,l,w,con=0,rang;
   int x,y,i,c, d2, d3, ry, crij, ckol, nl, wl, ander;
   int d,delta,cry;

   unsigned long kode;

   char  buf[80],buff[10];

   struct m_type * ma;
   struct m_type * fma;
   struct m_type * cur, * cur2;
   struct rccoord opos,ipos;

   unsigned int ccwedge[16];

    for (i=0;i<16;i++)
	   ccwedge[i]= centerrec.cwedge[i];

   /* matrix op scherm dispmat(); */
   dispmat();     /* display die-case on screen */
   do {
      /* count empty matrices : */
      for (ma = matrix, v1=0, leeg=0; ma != NULL; ma = ma ->_next) {
	  r = ma -> row; k = ma -> col;
	  if (k<17) {
	     v2 = k + r * 17;
	     /* printf(" r %2d k%2d v1 %3d v2 %3d ",r,k,v2,v2); */
	     leeg += v2 - v1;
	     v1 = v2 + 1;
	     /* printf(" leeg %3d ",leeg); getchar(); */
	  }
      }
      /* sprintf(buf,"leeg: %3d ",leeg);
	 colorprint(23,50,0,buf);
       */
      /* mogelijkheden:
	  leeg == 255
	  0 < leeg && leeg < 255
	  leeg = 0
       */
      if (leeg == 255) {
	 /* er is geen enkele matrijs
	    alleen plaatsen is mogelijk
	  */
	 sprintf(buf,"             place = 2            end = 0  ");
      } else if ((0<leeg) && (leeg <255)) {
	 sprintf(buf," remove = 1  place = 2  add  = 3  end = 0  ");
      } else {
	 sprintf(buf," remove = 1  add   = 3          end = 0  ");
      }

      colorprint(24,1,0,buf);

      opos = _gettextposition();
      ipos = opos;

      /*sprintf(buf,"pos = %2d,%2d",(int) opos.row,(int) opos.col);
      colorprint(24,60,0,buf);*/

      c = l2_int(-1,3,ipos.row,ipos.col); /* getchar();*/
      if (c == 0 ) {
	  doorgaan = 0 ;
      } else {
	  switch (c) {
	     case 1: /* matrijs wordt buitenmatrijs */
		if (leeg == 255 ) break; /* geen matrijs beschikbaar */
		sprintf(buf," remove ");
		colorprint(23,1,0,buf);
		do {  /* verwijderen */
		   sprintf(buf,"matrix  row      ");
		   colorprint(23,9,0,buf);
		   crij = l2_int(1,MAXRIJ+1,23,24);
		   for(i=0,nl=0; i<=16;i++){
		      nl += bezet[crij-1][i];
		   }
		} while ( ! nl );
		do {
		   sprintf(buf,"kolom :   ");
		   colorprint(23,28,0,buf);
		   ckol = vraagkolom(23,35);
		   _bezet = bezet[crij-1][ckol-1];
		} while ( ! _bezet );

		r=0; k=0; found =0; fma =NULL;
		rang = crij* 17 + ckol - 18;

		for (ma = matrix;
		   ma != NULL && ! found &&  ( r*17+k < rang ) ;
				   ma = ma ->_next) {
		   r = ma -> row; k = ma -> col;
		   if ( r*17+k == rang ) {
		      found = 1;
		      fma = ma;
		   }
		    /*
		    sprintf(buf," f %2d r %2d crij %2d k%2d ckol %2d l=%1c               ",
		       found, r+1,crij,k+1,ckol, ma -> ligature[0]);
		    aandacht(21,1,buf);
		    */
		}

		if (! found ) break;



		sprintf(buf,"fma r %2d k%2d l=%1c dikte %2d wig %2d        ->",
			fma-> row +1 ,fma->col+1, fma -> ligature[0],
			fma-> width, ccwedge[fma->row] );
		aandacht(21,1,buf);

		 r = fma -> row;  k = fma -> col;

		 sprintf(buf,"   ");      /* leeg maken display */
		 colorprint(r+6, k*4+6, 0 , buf );
		 bezet[r][k] = 0;


		 /* zoek de plaats waar de matrijs moet komen in de rij
		   het wordt de laatste buitenmatrijs ....
		 */

		 /* start sourch with the first after fma in the row
		    look for the last one....
		 */
		/* zoeken naar de rij waar de matrijs eigenlijk hoort */
		cry = crij;
		for (i=0,d=30;i<14;i++){
		    delta = abs(ccwedge[i] - fma->width);
		    if (delta<d) {
		       d= delta;
		       cry = i;
		/*sprintf(buf," cry = %2d delta %2d d %2d i= %2d ",cry,delta,d,i);
		aandacht(21,0,buf);
		 */
		    }
		}

		sprintf(buf," cry = %2d delta %2d d %2d ",cry,delta,d);
		aandacht(21,0,buf);
		if (cry != crij ) {
		  sprintf(buf," cry = %2d crij = %2d        !!!!!!!       !!!!",
				cry,crij);
		  aandacht(21,0,buf);
		  /* crij = cry;*/
		}
		for ( cur = fma-> _next ;
			cur != eindmatrix && cur != NULL &&
			     (( (r=cur->row) +1) == crij ) ;
			cur = cur -> _next ) {

		    k = cur -> col; /* dit stijgt tot .... */
		    /*
		    sprintf(buf,"verder zoeken: r %2d cr %2d k%2d  l=%1c ",
			 r+1,crij,k+1, cur -> ligature[0]);
		    aandacht(21,1,buf);
		    */
		}

		/*
		   sprintf(buf," cur r %2d cr %2d k%2d  l=%1c ",
			 cur -> row +1, crij, cur -> col+1,
			 cur -> ligature[0]);
		   aandacht(21,1,buf);
		 */
		/* mogelijkheden :
		   eerst van plaats verwisselen
		   daarna de gietcode aanpassen...
		   ook moet in het raampje de plaats worden vrijgemaakt,
		   door op de oude plaats drie spaties te printen
		 */

		if ( cur == NULL ) {
		    cur = eindmatrix;
		    ( fma -> _fore ) -> _next = fma -> _next;
		    if (fma -> _next != NULL) {
		       ( fma -> _next ) -> _fore = fma -> _fore;
		    }
		    fma -> _fore = cur;
		    fma -> _next = cur -> _next;     /* dat was NULL */
		    cur -> _next = fma;
		    eindmatrix = fma;
		}
		else if (fma == eindmatrix ) {
		       /*   laatste matrijs in het raam ...
			dan moet alleen het record van fma aangepast...
		       */
		    for (cur = fma -> _fore, found =0;
		       cur -> row == (crij-1) && ! found;
		       cur = cur -> _fore) {
		       found = ( cur -> width == ccwedge[crij-1] );
		    }
		    if ( ((ma -> _fore) -> row ) == (fma -> row) ) {
			/* zoek de laatste die niet te groot in de
			   rij staat, want die wordt met een S-naald
			   gegoten...
			 */

			fma -> col = (fma -> _fore) -> col + 1;
			if (fma -> col < 17 ) fma -> col = 17;
			w = (fma -> _fore) -> width;
			if (w == ccwedge[crij-1] )
			      fma -> code = ( fma -> _fore ) -> code;

		    }
			/* alleen terugzoeken is genoeg
			    maar we hoeven enkel te kijken naar het record
			    daarvoor, en de pointers hoeven ook niet omgezet;
			    enkel moet de code aangepast, en dat geldt voor alle
			    buitenmatrijzen....
			 */
		} else {
		    /* eerst fma ertussen uithalen */
		    ( fma -> _fore ) -> _next = fma -> _next;
		    ( fma -> _next ) -> _fore = fma -> _fore;
		    /* daarna fma voor cur plaatsen */
		    fma -> _fore = cur -> _fore;
		    fma -> _next = cur;
		    cur -> _fore            = fma;
		    (fma -> _fore) -> _next = fma;
			/* record fma aanpassen */
		    k = (int) max (17, (fma -> _fore) -> col +1 );
		    fma -> col = k;
			/* sprintf(buf," k wordt %2d ",k); aandacht(21,0,buf); */
		    bezet[r][fma -> col]=1;
		}

		 /*
		  for(cur2=matrix; cur2 -> row < crij; cur2 = cur2 -> _next){
		     if (cur2->row >= crij-1) {
			sprintf(buf,"nagaan 1: r=%2d k=%2d l=%1c ....",
			    cur2->row,cur2->col,cur2->ligature[0]);
			aandacht(21,0,buf);
		     }
		  }
		  */
		 /* de gietcode gaat ook veranderen
		     (width == ccwedge.[crij-1]) ||
			    (width == ccwedge.[crij-1]+5)

		     als: width > ccwedge.[crij-1]

			dan moet er met een S-naald gegoten worden
			de uitvulling blijft gelijk... die hoort bij de
			matrijs

		  */

		wl = ccwedge[crij-1];
		for (found =0 , cur = NULL, cur2=fma->_fore;
				  !found && cur2 -> _fore != NULL;
				       cur2=cur2->_fore) {
		    if ( ( cur2 -> col <= 16) && (wl == cur2 -> width)
				&& (cur2->ligature[0] !='#') ) {
			found = 1; cur = cur2;
		    }
		}
		d2 = ccwedge[crij-1];  d3 = d2 +5;
		sprintf(buf,"hier gaat het mis w %2d ",cur->width );
		aandacht(21,0,buf);

		if ( (cur->width == d2 ) ||
			  (cur->width == d3  )) {
		     fma -> code = cur -> code;
		} else
		     if ( cur->width != d2 ){

		     fma -> code = cur -> code;
		     fma -> code |= _Snaald;
		}
		 /*
		    als de matrijs in de rij buitenmatrijs wordt
		    dan
		    moeten alle codes van de buitenmatrijzen veranderen
		    ... want die staan daaraan gekoppeld...
		  */
		if (fma -> col >17) {
		    cur2 = fma;
		    for (i= (fma->col -1); i>=17; i--) {
			cur2 = cur2 -> _fore;
			cur2 -> code &= ~_Snaald;   /* alleen Snaald aanlaten */
			cur2 -> code |= cur -> code;
		    }
		}
		break;

	     case 2: /* plaatsen buitenmatrijs op lege plaats */
		if (!leeg) break; /* geen plaats voor nieuwe matrijs */
		sprintf(buf," place ");
		colorprint(23,1,0,buf);
		do {
		   sprintf(buf,"matrix  row      ");
		   colorprint(23,8,0,buf);
		   crij = l2_int(1,MAXRIJ+1,23,24);
		   for(i=0,nl=0;i<=16;i++){
		      nl += bezet[crij-1][i];
		   }
		} while ( nl == 17 );
		  /* < 17 => dan is er 'n lege plaats in de rij*/
		do {
		   sprintf(buf,"kolom :");
		   colorprint(23,28,0,buf);
		   ckol = vraagkolom(23,35);
		   _bezet = bezet[crij-1][ckol-1];
		   /*
		   sprintf(buf," crij %2d ckol %2d bezet %2d ",crij,ckol,_bezet);
		   aandacht(23,40,buf);
		   */
		} while ( _bezet );

		r=0; k=0; found =0; fma =NULL;
		rang = crij* 17 + ckol - 18;
		for (ma = matrix;
		   ma != NULL && ! found &&  ( r*17+k < rang ) ;
				   ma = ma ->_next) {
		   r = ma -> row; k = ma -> col;
		   if ( r*17+k == rang ) {
			found = 1; fma = ma;
		   } else {
			cur = ma;
		   }
		   /*    sprintf(buf," f %2d r %2d crij %2d k%2d ckol %2d l=%1c               ",
		       found, r+1,crij,k+1,ckol, ma -> ligature[0]);
		    aandacht(21,1,buf);
		    */
		}
		if (found ) {
		   /*
		   sprintf(buf," gevonden !! r %2d k %2d l=%1c ",
			   fma->row+1,fma->col+1,
			   fma->ligature[0]);
		   colorprint(21,1,0,buf);
		   */
		 } else {
		   /*
		   sprintf(buf," niet gevonden ! cur = %1c k = %2d",cur->ligature[0],
			 cur -> col );
		   colorprint(21,1,0,buf);
		   */
			 fma = cur;
		 }
		 if (!found) fma = cur;
		 /*
		 _settextcursor( DOUBLEUNDERLINE );
		 _displaycursor( _GCURSORON );
		 getchar();
		 */

		/* waar kijkt ma naar ? */
		/*
		sprintf(buf,"ma kijkt naar: f %2d r %2d crij %2d k%2d ckol %2d l=%1c               ",
		       found, r+1,crij,k+1,ckol, ma -> ligature[0]);
		aandacht(21,1,buf);
		*/
		/* bepalen wat daar moet komen */
		/* disp_buit rij
		   invoeren $ en soort:
		      daarna zoeken in buitenmatrijzen
		*/

		ander = 0;
		do { /* zoek tot een rij gekozen is geen ander... */
		   do { /* kies rijnummer tot nrij > 0 */
		      sprintf(buf," buitenmatrijzen in rij ");
		      colorprint(23,0,0,buf);
		      opos = _gettextposition();
		      ry = l2_int(1, MAXRIJ+1,opos.row,opos.col);

		      sprintf(buf,"                                                                      ");
		      for (i=21;i<=24;i++) colorprint(i,1,0,buf);

		      /* dit willen we wegschrijven */

		      ry1.p = NULL;
		      disp_buit( ry );

		      if (ry1.p != NULL) {
			 /**/
			 sprintf(buf,"                                                           ");
			 colorprint(23,1,0,buf);
			 sprintf(buf,"aantal %2d m =",ry1.n);
			 colorprint(23,1,0,buf);
			 for (i=0;i<2;i++)
			    buf[i] = ry1.p -> ligature[i]; buf[3]='\0';
			 colorprint(23,16, ry1.p -> kind, buf);
			 /**/
		      } else {
			 /*
			 sprintf(buf,"aantal buiten =%2d ",ry1.n);
			 colorprint(24,50,0,buf);
			 */
		      }
		   } while (! ry1.n );
		   /* vraag nummer buitenmatrijs = ander
			plaats goed zetten....
		   */
		   sprintf(buf," nummer buitenmatrijs           ");
		   colorprint(23,0,0,buf);
		   /* _settextposition(23,24); opos = _gettextposition();*/
		   ander = l2_int(0, ry1.n ,23,24);
		} while ( ! ander );

		/* vervang buitenmatrijs : */

		cur = ry1.p;
		bezet[ry-1][16+ry1.n]=0;

		for (i=1;i<ander;i++) {   /* zoek record buitenmatrijs */
		      cur = cur -> _next;
		/*      sprintf(buf,"i %2d l = %1c ",i,cur->ligature[0]);
		      aandacht(21,0,buf);*/
		}
		/*
		sprintf(buf,"i %2d l = %1c ",i,cur->ligature[0]);
		aandacht(21,0,buf);
		 */

		/* weghalen cur uit rij */

		(cur -> _next ) -> _fore = cur -> _fore;
		(cur -> _fore ) -> _next = cur -> _next;

		/* cur komt VOOR fma */

		cur -> _fore =

		      fma -> _fore;

		cur -> _next = (fma -> _fore) -> _next;
		cur -> col = ckol - 1 ;
		cur -> row = ry - 1;

		/* cur -> code */

		kode &= _Snaald;
		kode |= kcodes[cur -> col];
		kode |= rcodes[cur -> row];
		cur -> code = kode;

		dispma( cur );




		/*
		sprintf(buf,"%1c%1c%1c",cur->ligature[0],cur->ligature[1],
			 cur->ligature[2]);*/      /* vullen display */
		/*
		colorprint( (ry-1)+6, (ckol-1)*4+6, cur->kind , buf );
		*/

		/* adjust pointers */

		(cur -> _fore) -> _next = cur;
		ma -> _fore = cur;
		bezet[crij-1][ckol-1] = 1;

		/*  shows the resting order * /
		for (i = 0, cur2 = ry1.p ; i < ( ry1.n - 1) ;i++) {
		    cur2 -> col = (i==0) ? 17 : ( cur2 -> _fore ) -> col + 1;
		    sprintf(buf," i: %2d cur l %1c col %2d ",i,cur->ligature[0],cur->col);
		    aandacht(21,0,buf);
		    cur2 = cur2 -> _next;
		}
		/ * */

		weergeven(matrix , 25, 21,0);

		/* bezet[rij-1][c?] = 0; */
			/*
			disp_buit(crij-1);
			cur = ry1.p
			 */
				/* struct rijtje ry1.p
				wijst naar begin van een rij records
				*/
			/*  ry1.n; */ /* aantal records rijtje lang */




		/* cur -> record */
		/* verwijderen uit de buitenmatrijzen */
		/* voeg hem tussen */
		/* pas het rijtje buitenmatrijzen aan

		   code hoeft niet te veranderen, want de
		   matrijs waarmee ze gegoten worden blijft staan
		   alleen de rangrummers moeten aangepast
		   en het bezetarray...
		*/

		break;

	     case 3: /* add matrix to the case */

		sprintf(buf," add    ");
		colorprint(23,1,0,buf);

		do {
		   sprintf(buf,"matrix  row      ");
		   colorprint(23,10,0,buf);
		   crij = l2_int(1,MAXRIJ+1,23,24);
		   for(i=0,nl=0;i<=16;i++){
		      nl += bezet[crij-1][i];
		   }
		} while (!nl); /* er moet er minstens 1 matrijs staan */

		/* different sourch */

		found = 0; r = -1; k=-1;
		fma = NULL;
		for (ma = matrix ; ma != NULL && ((r+1) < crij) ;
			 ma=ma -> _next){
		    r = ma -> row;
		    k = ma -> col;
		    sprintf(buf," f %2d r %2d cr %2d k%2d  l=%1c ",
		       found, r+1,crij,k+1, ma -> ligature[0]);
		    colorprint(21,1,0,buf);
		    _settextcursor( DOUBLEUNDERLINE );
		    _displaycursor( _GCURSORON );
		    getchar();
		}
		 /* start sourch with the first in the row
		    zoek de laatste....
		 */

		 for (     ; ma != NULL && ((r+1) == crij ) ;
			ma = ma -> _next) {
		    r = ma -> row;
		    k = ma -> col; /* dit stijgt tot .... */
		    fma = ma;
		    sprintf(buf," f %2d r %2d cr %2d k%2d  l=%1c ",
		       found, r+1,crij,k+1, ma -> ligature[0]);
		    colorprint(21,1,0,buf);
		    _settextcursor( DOUBLEUNDERLINE );
		    _displaycursor( _GCURSORON );
		    getchar();
		 }

		 /* mogelijkheden :
		  1) de rij is leeg !
		       ma kijkt naar de laatste voor de rij
		       tussenvoegen, en op plaats (crij-1),16 zetten
		       code van deze plaats
		       - verwijstabel aanpassen
		       - bezet aanpassen
		  2) ma == NULL
		       achtervoegen
		  3) fma kijkt naar de laatste in de rij
		       achtervoegen,
		      -
		 */
		 if (crij == 17 ) {   /* add at the end */
		    cur = vrijmaken();
		    cur -> _next = NULL;
		    cur -> _fore = eindmatrix;
		    fma = eindmatrix;
		    eindmatrix -> _next = cur;
		    eindmatrix = cur;
		    found = 1;
		 }   /* points to record after the place */
		 k = fma -> col;
		 sprintf(buf," f %2d r %2d cr %2d k%2d     l=%1c ",
		     found, r+1,crij,k+1, fma -> ligature[0]);
		 colorprint(21,1,0,buf);
		 _settextcursor( DOUBLEUNDERLINE );
		 _displaycursor( _GCURSORON );
		 getchar();

		 /* toevoegen buitenmatrijs */
		 /* cur
		   sprintf(buf,"lig:   ");
		   colorprint(23,39,0,buf);
		   do {
		       colorprint(23,45,0,"   ");
		       _settextposition(23,45);
		       get_line2(23,45,buff , 3 );
		   } while (buff[0] == 10 );
		   mcode = fma -> code;
		   for (i=0; i<2 && buff[i] != 10; i++){
		      cur -> ligature[i]=buff[i];
		   }
		   code maken:
		      zoeken in de rij daarvoor
		      als de hele rij leeg is.... gaat het mis
		*/


		 break;
	  }
	  _settextcursor( DOUBLEUNDERLINE );
	  _displaycursor( _GCURSORON );
	  getchar();
      }

   } while (doorgaan);

   /*
      kiezen plaats in matrix
      rij,           0 < rij <16
      kolom kiezen,  0 < kolom <18
      volle plaats:
	 verwijderen matrijs uit de matrix:
	 wordt een buitenmatrijs in de rij waar hij hoort...
      lege plaats:
	 die kan gevuld worden:
	 1) nieuwe matrijs:
	    vrijmaken record
	    inlezen $
	    inlezen dikte
	    berekenen uitvulling
	    berekenen code
	    tussenvoegen
	 2) buitenmatrijs:
	    vraag rij waaruit de matrijs moet komen
	    bepaal welke buitenmatrijs
	    - verwijder buitenrecord uit de rij
	    - voeg buitenrecord tussen in de rij
	    - pas de display aan
   */
   terug:
   return (1);
}  /* einde _change_matrix() colorprint( wedge[ */

