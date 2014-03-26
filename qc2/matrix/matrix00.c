/*

    programma om matrijenramen in te lezen

    Matrix


*/

#include <stdio.h>
#include <conio.h>
#include <io.h>
#include <dos.h>
#include <stdlib.h>
#include <string.h>
#include <graph.h>

#define MATMAX     292
#define RIJAANTAL   17
#define KOLAANTAL   16

typedef struct matrijs {
     char     lig[4];  /* string present in mat
			  4 bytes: for unicode
			  otherwise 3 asc...
			*/
     unsigned char srt;      /* 0=romein 1=italic 2= kk 3=bold
				4=superieur
				5=inferieur
			      */
     unsigned int  w;        /*

	      in a future version, this could be an int:
		   10 * 23 = 230
	      calculations in 1/10 of an unit... is accurate enough
		 width in units  */

     unsigned char mrij  ;   /* place in mat-case   */
     unsigned char mkolom;   /* place in mat-case   */
};

/*
struct matrijs matrix[
MATMAX
]
;
*/

struct matrijs far matrix[ 322 ] = {

/* missing accents */
"\214",0, 5, 0, 9,"\213",0, 5, 0, 9,"\215",0, 5, 0, 9,
"\240",0, 5, 0, 9,"\203",1, 8, 2,11,"\204",1, 8, 2,11,
"\205",1, 8, 2,11,"\240",1, 8, 2,11,"\210",1, 5, 0, 6,
"\211",1, 5, 0, 6,"\212",1, 5, 0, 6,"\202",1, 5, 0, 6,
"\223",1, 6, 1, 2,"\224",1, 6, 1, 2,"\225",1, 6, 1, 2,
"\242",1, 6, 1, 2,""    ,0,18,15,16,

/* missing accents o^" */
"\223",1, 7, 1, 2,"\224",1, 7, 1, 2,"\225",1, 7, 1, 2,
"\242",1, 7, 1, 2,""    ,0,12, 1, 4,""    ,0,12,10, 5,


"\207",1, 5, 0, 0,"`"   ,0, 5, 0, 1,"i"   ,0, 5, 0, 2,
"j"   ,0, 5, 0, 3,"f"   ,1, 5, 0, 4,""    ,0, 5, 0, 5,
"l"   ,0, 5, 0, 6,"c"   ,1, 5, 0, 7," "   ,0, 5, 0, 8,
"i"   ,1, 5, 0, 9,"l"   ,1, 5, 0,10,"r"   ,1, 5, 0,11,
"s"   ,1, 5, 0,12,"e"   ,1, 5, 0,13,"j"   ,1, 5, 0,14,
"'"   ,1, 5, 0,15,""    ,0, 5, 0,16,

"'"   ,0, 5, 1, 0,";"   ,0, 6, 1, 1,"I"   ,0, 6, 1, 2,
"J"   ,0, 6, 1, 3,"f"   ,0, 6, 1, 4,""    ,0, 6, 1, 5,
"-"   ,0, 6, 1, 6,"t"   ,0, 6, 1, 7," "   ,1, 6, 1, 8,
"s"   ,0, 6, 1, 9,","   ,0, 5, 1,10,"."   ,0, 5, 1,11,
"t"   ,1, 5, 1,12,"."   ,1, 5, 1,13,","   ,1, 5, 1,14,
":"   ,1, 6, 1,15,"o"   ,1, 6, 1,16,

""    ,0, 7, 2, 0,""    ,0, 7, 2, 1,";"   ,1, 6, 2, 2,
"!"   ,1, 7, 2, 3,""    ,0, 7, 2, 4,":"   ,0, 7, 2, 5,
"!"   ,0, 7, 2, 6,"r"   ,0, 7, 2, 7,"?"   ,0, 7, 2, 8,
"a"   ,1, 7, 2, 9,"g"   ,1, 7, 2,10,"k"   ,1, 7, 2,11,
"v"   ,1, 7, 2,12,"x"   ,1, 7, 2,13,"y"   ,1, 7, 2,14,
"I"   ,1, 7, 2,15,"J"   ,1, 7, 2,16,

"("   ,1, 8, 3, 0,")"   ,1, 8, 3, 1,"b"   ,1, 8, 3, 2,
"d"   ,1, 8, 3, 3,"h"   ,1, 8, 3, 4,"n"   ,1, 8, 3, 5,
"\244",1, 8, 3, 6,"p"   ,1, 8, 3, 7,"q"   ,1, 8, 3, 8,
"u"   ,1, 8, 3, 9,"z"   ,1, 8, 3,10,"oe!" ,1, 8, 3,11,
"ij"  ,1, 8, 3,12,"fl"  ,1, 8, 3,13,"fj"  ,1, 8, 3,14,
"fi"  ,1, 8, 3,15,"\221",1, 8, 3,16,

""    ,0, 9, 4, 0,""    ,0, 9, 4, 1,"/"   ,0, 9, 4, 2,
"\365",0, 9, 4, 3,"\364",0,11, 4, 4,"?"   ,1, 8, 4, 5,
"\200",2, 9, 4, 6,"z"   ,0, 8, 4, 7," "   ,2, 9, 4, 8,
"a"   ,0, 8, 4, 9,"e"   ,0, 8, 4,10,"c"   ,0, 8, 4,11,
"\226",1, 8, 4,12,"\243",1, 8, 4,13,"\227",1, 8, 4,14,
"ff"  ,1, 8, 4,15,""    ,0, 9, 4,16,

""    ,0, 9, 5, 0,"1"   ,1, 8, 5, 1,""    ,0, 8, 5, 2,
"2"   ,1, 8, 5, 3,"3"   ,1, 8, 5, 4,"4"   ,1, 8, 5, 5,
"5"   ,1, 8, 5, 6,"6"   ,1, 8, 5, 7,"\202",0, 8, 5, 8,
"\212",0, 8, 5, 9,"\211",0, 8, 5,10,"\210",0, 8, 5,11,
"\201",1, 8, 5,12,"7"   ,1, 8, 5,13,"8"   ,1, 8, 5,14,
"0"   ,1, 8, 5,15,"9"   ,1, 8, 5,16,

""    ,0, 9, 6, 0,""    ,0, 9, 6, 1,""    ,0, 9, 6, 2,
"1"   ,0, 9, 6, 3,"2"   ,0, 9, 6, 4,"\240",0, 8, 6, 5,
"\205",0, 8, 6, 6,"\204",0, 8, 6, 7,"\203",0, 8, 6, 8,
"3"   ,0, 9, 6, 9,"4"   ,0, 9, 6,10,"5"   ,0, 9, 6,11,
"6"   ,0, 9, 6,12,"7"   ,0, 9, 6,13,"8"   ,0, 9, 6,14,
"9"   ,0, 9, 6,15,"0"   ,0, 9, 6,16,

""    ,0, 9, 7, 0,""    ,0,10, 7, 1,"\243",0,10, 7, 2,
"\227",0,10, 7, 3,"\201",0,10, 7, 4,"\226",0,10, 7, 5,
"b"   ,0,10, 7, 6,"d"   ,0,10, 7, 7,"n"   ,0,10, 7, 8,
"g"   ,0,10, 7, 9,"h"   ,0,10, 7,10,"p"   ,0,10, 7,11,
"ij"  ,0,10, 7,12,"fj"  ,0,11, 7,13,"\244",0,10, 7,14,
""    ,0,10, 7,15,"S"   ,1,10, 7,16,

""    ,0,10, 8, 0,""    ,0,10, 8, 1,"\242",0,10, 8, 2,
"\225",0,10, 8, 3,"\224",0,10, 8, 4,"F"   ,0,10, 8, 5,
"S"   ,0,10, 8, 6,"o"   ,0,10, 8, 7,"u"   ,0,10, 8, 8,
"v"   ,0,10, 8, 9,"k"   ,0,10, 8,10,"q"   ,0,10, 8,11,
"x"   ,0,10, 8,12,"y"   ,0,10, 8,13,"\223",0,10, 8,14,
"\256",0,10, 8,15,"\257",0,10, 8,16,

""    ,0,11, 9, 0,""    ,0,11, 9, 1,""    ,0,11, 9, 2,
""    ,0,11, 9, 3,"ff"  ,0,11, 9, 4,"fi"  ,0,11, 9, 5,
"fl"  ,0,10, 9, 6,"L"   ,0,11, 9, 7,"P"   ,0,11, 9, 8,
"m"   ,1,11, 9, 9,"w"   ,1,11, 9,10,"E"   ,1,11, 9,11,
"F"   ,1,11, 9,12,"P"   ,1,11, 9,13,"fk"  ,1,11, 9,14,
"fh"  ,1,11, 9,15,"fb"  ,1,11, 9,16,


/*
""    ,0,12,10, 0,""    ,0,12,10, 1,""    ,0,12,10, 2,
""    ,0,12,10, 3,""    ,0,12,10, 4,""    ,0,12,10, 5,
*/

""    ,0,12,10, 6,""    ,0,12,10, 7,"E"   ,0,12,10, 8,
"\221",0,12,10, 9,""    ,0,12,10,10,""    ,0,12,10,11,
"B"   ,1,12,10,12,"L"   ,1,12,10,13,"T"   ,1,12,10,14,
"ffi" ,1,12,10,15,"ffl" ,1,12,10,16,

""    ,0,13,11, 0,""    ,0,13,11, 1,"\245",0,16,11, 2, /* N~ */
"fh"  ,0,16,11, 3,"fk"  ,0,16,11, 4,"fb"  ,0,16,11, 5,
"ffi" ,0,15,11, 6,"ffl" ,0,15,11, 7,"B"   ,0,13,11, 8,
"T"   ,0,13,11, 9,"Z"   ,0,13,11,10,""    ,0,13,11,11,
"\200",1,13,11,12,"C"   ,1,13,11,13,"K"   ,1,13,11,14,
"R"   ,1,13,11,15,"Z"   ,1,12,11,16,

""    ,0,14,12, 0,""    ,0,14,12, 1,"&"   ,0,14,12, 2,
"R"   ,0,14,12, 3,"\200",0,14,12, 4,"A"   ,0,14,12, 5,
"C"   ,0,14,12, 6,"G"   ,0,14,12, 7,"K"   ,0,14,12, 8,
"V"   ,0,14,12, 9,"Y"   ,0,14,12,10,"oe!" ,0,14,12,11,
"A"   ,1,14,12,12,"G"   ,1,14,12,13,"V"   ,1,14,12,14,
"Y"   ,1,14,12,15,"&"   ,1,14,12,16,

""    ,0,15,13, 0,""    ,0,15,13, 1,"H"   ,0,15,13, 2,
"Q"   ,0,16,13, 3,"U"   ,0,16,13, 4,"D"   ,0,15,13, 5,
"w"   ,0,15,13, 6,"m"   ,0,16,13, 7,"N"   ,0,16,13, 8,
"O"   ,0,16,13, 9,"D"   ,1,15,13,10,"H"   ,1,15,13,11,
"N"   ,1,15,13,12,"O"   ,1,15,13,13,"Q"   ,1,15,13,14,
"U"   ,1,15,13,15,"X"   ,1,15,13,16,

""    ,0,18,14, 0,""    ,0,18,14, 1,""    ,0,18,14, 2,
""    ,0,18,14, 3,"X"   ,0,15,14, 4,"OE!" ,0,19,14, 5,
"\222",0,18,14, 6,"M"   ,0,18,14, 7,""    ,0,18,14, 8,
"W"   ,0,21,14, 9,""    ,0,18,14,10,"W"   ,1,19,14,11,
"OE!" ,1,21,14,12,"\222",1,18,14,13,"M"   ,1,18,14,14,
"---" ,0,18,14,15," "   ,4,18,14,16,


":"   ,2, 7, 2, 6,";"   ,2, 7, 2, 7,"!"   ,2, 6, 2, 2,
"?"   ,2, 9, 8,14,"."   ,1, 5, 0,13,"."   ,2, 5, 0,13,
","   ,1, 5, 0,14,","   ,2, 5, 0, 3,"\047",2, 5, 0, 4,
"`"   ,2, 5, 0, 4,"\047",1, 5, 0, 4,""    ,1, 5, 0,14,
"-"   ,1, 6, 1, 6,"-"   ,2, 6, 1, 6,"--"  ,0, 9, 6, 0,
"--"  ,2, 9, 6, 0,"---" ,1,18,14,15,"---" ,2,18,14,15,
"\256",0, 9, 2, 3,"\257",0, 9, 2, 4,"\256",2, 9, 2, 3,
"\257",2, 9, 2, 4

    /* matmax 17*16 + 50 = 322  * ] =


~!@#$%^&*()_+
`1234567890-=
QWERTYUIOP{}|
qwertyuiop[]\
ASDFGHJKL:"
asdfghjkl;'
|ZXCVBNM<>?
\zxcvbnm,./

*/

};






struct matrijs filerec2; /*record for die-case files
			    extention: 'die'

*/

char name[15]="Dante 592     ";

typedef struct naamrecord {
     char          naam_str[25]; /* name of the font */
     unsigned int  series;       /* monotype series code */
     unsigned int  set;          /* 4 times the set */
     unsigned char corps;        /* corps */
     unsigned int  aantal;       /* number of records in font-file */
}
naam1,     /* input file */
naam2,     /* output file */
filerec1 ; /* record file with extension: fnn */

/*
void kiesfont();
 */



unsigned char wig[RIJAANTAL]= {
      5,6,7,8,9,9,9,10,10,11,12,13,14,15,18,18
      };

void intro();
void menu();

void leeg_matrix();
void cls();


void print_at(int rij, int kolom, char *buf);

void print_at(int rij, int kolom, char *buf)
{
     _settextposition( rij , kolom );
     _outtext( buf );
}



void disp_mat(struct matrijs m);
void disp_matrix();
void write_file();
void read_file();

void hex_main();

void wis_mat(int r, int c);
void read_mat(int r, int c);

void read_mat(int r, int c)
{
;
}
void wis_mat(int r, int c)
{
;
}

void nieuw();
void read_file();
void write_file();
void display_file(); /* display file */
void adjust_file();
void nieuw()
{
   char c;
   do {
     cls();
     printf("Nieuw");
     c=getchar();
   }
     while (c !='#');
}
void read_file()
{
   char c;

   /* read name */
   /* open file */
   /* read all records */
   /* display file */

   do {
     cls();
     printf("read file");
     c=getchar();
   }
     while (c !='#');
}

void write_file()
{
   char c;

   do {
     cls();
     printf("write file");
     c=getchar();
   }
     while (c !='#');
}

void display_file()
{
   char c;
   do {
     cls();
     printf("display file");
     c=getchar();
   }
     while (c !='#');
;
}
void adjust_file()
{
   char c;
   do {
     cls();
     printf("adjust file ");
     c=getchar();
   }
     while (c !='#');
}

void display_matrix();
void display_matrix()
{
    cls();
    printf("function Display matrix ");
    getchar();
}

#include <c:\qc2\matrix\monofnts.c>

void menu()
{

    char com;

    do {
      cls();
      printf("\n\n\n\n");
      printf("         Program Matrix  \n\n");
      printf("    version 0.0.1  date: 20-01-06 \n\n");
      printf("                 new file = n \n");
      printf("                read file = r \n");
      printf("               write file = w \n");
      printf("             display file = d \n");
      printf("           adjust diecase = a \n");
      printf("         standard diecase = s \n");
      printf("                  command = ");
      com = getchar();
      switch ( com) {
	 case 'n' :
	     nieuw();
	     /* wis diecase */
	     /* read all places */
	     /*  display all mats after reading */
	     break;
	 case 'r' :
	     read_file();
	     break;
	 case 'w' : /* write file */
	     write_file();
	     /* read new filenaam */
	     /* open file */
	     /* write file */
	     /* close file */
	     break;
	 case 'd' :
	     disp_matrix(); /* display file */
	     break;
	 case 'a' :
	     adjust_file();
	     /* display file */
	     /* read mat */
	     /* write mat in file */
	     break;
	 case 's' : /*standard diecases */
	     /*
	     kiesfont(); */
	     /*
	     cls();
	     printf("chose from standards ");
	     getchar();
	     */
	     /* chose from a number of diecases */
	     /* fil matrix */

	     break;
      }
    }
       while (com != '#' );

    ;
}

void disp_mat(struct matrijs m)
{
     print_at( m.mrij+4,m.mkolom*4 +7,"");
     switch ( m.srt){
	 case 0: printf(" "); break;/* roman */
	 case 1: printf("/"); break;/* italic */
	 case 2: printf("."); break;/* small caps */
	 case 3: printf(":"); break;/* bold */
	 case 4: printf("^"); break;/* superieur */
	 case 5: printf("_"); break;/* inferieur */
     }
     printf("%1c%1c%1c",m.lig[0],m.lig[1],m.lig[2]);
}


void cls()
{
   _clearscreen( _GCLEARSCREEN );
}


void leeg_matrix()
{
    int i, j;

    printf("Leeg matrix ");

    for (i=0;i<292 ;i++) {
	matrix[i].lig[0]= ' ';
	matrix[i].lig[1]= ' ';
	matrix[i].lig[2]= ' ';
	matrix[i].lig[3]= ' ';

	matrix[i].srt    = 0;
	matrix[i].w      = 0;

	matrix[i].mrij   = (char) (i % 17) ;
	matrix[i].mkolom = (char) (i / 17) ;
	/*
	cls();
	printf(" i= %3d lig = %4c srt %2d val %2d rij %2d kol %2d ",i,matrix[i].lig,
	   matrix[i].srt, matrix[i].w, matrix[i].mrij, matrix[i].mkolom);
	if (getchar()=='#') exit(1);
	 */
    }

    printf("Matrix is empty ");
    if (getchar()=='#') exit(1);

}

void disp_matrix()
{
   int i,j;

   float size = 12;
   int  set_font = 43;

   cls();
   printf("Disp matrix: ");
   getchar();
   cls();
   printf("      Font: ");
   for (i=0;i<15; i++) printf("%1c",name[i]);
   printf("  points %6.2f set %7.2f \n\n",name,size, .25 * ((float)set_font) );
   printf("        NI  NL  A   B   C   D   E   F   G   H   I   J   K   L   M   N   O \n");
   /*
   printf("       123 123 123 123 123 123 123 123 123 123 123 123 123 123 123 123 123");
   getchar();
    */

   for (i=0;i<RIJAANTAL-1;i++) {
   printf("   %2d                                                                      %2d\n",
	     wig[i],i+1);
   }

   for (i=0;i<292; i++){
      disp_mat(matrix[i]);

      /*
      print_at( matrix[i].mrij+3,matrix[i].mkolom*4 +7,"");
      printf("%1c%1c%1c",matrix[i].lig[0],matrix[i].lig[1],matrix[i].lig[2]);
       */
   }
   print_at(20,1,"klaar");
   if (getchar()=='#') exit(1);

   /*
   for (i=0;i<10;i++){
       printf("i = %2d lig = %1c%1c%1c rij %2d kolom %2d srt %2d val %2d ",i,
	   matrix[i].lig[0],matrix[i].lig[1],matrix[i].lig[2],
	   (int) matrix[i].mrij,(int) matrix[i].mkolom,
	   matrix[i].srt, matrix[i].w);
       if (getchar()=='#') exit(1);
   }
    */


}

void intro()
{
    printf("   Matrix \n\n");
    printf("   version 0.0 \n\n");
    printf("   date : 17-01-2006 \n\n");
    printf("   reading matrix-files \n\n");
    if (getchar()=='#') exit(1);

}


main ()
{
    intro();
    menu();

    /*leeg_matrix();*/

    disp_matrix();
    printf(" einde programma ");
    getchar();
    exit(1);
    hex_main();
    if (getchar()=='#') exit(1);
}

/* RECORDS2.C illustrates reading and writing of file records with the
 * following functions:
 *      fgetpos     fsetpos
 *
 * See RECORDS1.C for a version using fseek, rewind, and ftell.
''
	   Regular ASCII Chart (character codes 0 - 127)
000   (nul) 00 000   016  (dle) 10 020   032 sp 20 040   048 0 30 060
001   (soh) 01 001   017  (dc1) 11 021   033 !  21 041   049 1 31 061
002  (stx) 02 002   018  (dc2) 12 022   034 "  22 042   050 2 32 062
003  (etx) 03 003   019  (dc3) 13 023   035 #  23 043   051 3 33 063
004  (eot) 04 004   020  (dc4) 14 024   036 $  24 044   052 4 34 064
005  (enq) 05 005   021  (nak) 15 025   037 %  25 045   053 5 35 065
006  (ack) 06 006   022  (syn) 16 026   038 &  26 046   054 6 36 066
007  (bel) 07 007   023  (etb) 17 027   039 '  27 047   055 7 37 067
008  (bs)  08 010   024  (can) 18 030   040 (  28 050   056 8 38 070
009   (tab) 09 011   025  (em)  19 031   041 )  29 051   057 9 39 071
010   (lf)  0a 012   026   (eof) 1a 032   042 *  2a 052   058 : 3a 072
011  (vt)  0b 013   027  (esc) 1b 033   043 +  2b 053   059 ; 3b 073
012  (np)  0c 014   028  (fs)  1c 034   044 ,  2c 054   060 < 3c 074
013   (cr)  0d 015   029  (gs)  1d 035   045 -  2d 055   061 = 3d 075
014  (so)  0e 016   030  (rs)  1e 036   046 .  2e 056   062 > 3e 076
015  (si)  0f 017   031  (us)  1f 037   047 /  2f 057   063 ? 3f 077

	   Regular ASCII Chart (character codes 0 - 127)
064 @ 40 100   080 P 50 120  096 ` 60 140  112 p 70 160
065 A 41 101   081 Q 51 121  097 a 61 141  113 q 71 161
066 B 42 102   082 R 52 122  098 b 62 142  114 r 72 162
067 C 43 103   083 S 53 123  099 c 63 143  115 s 73 163
068 D 44 104   084 T 54 124  100 d 64 144  116 t 74 164
069 E 45 105   085 U 55 125  101 e 65 145  117 u 75 165
070 F 46 106   086 V 56 126  102 f 66 146  118 v 76 166
071 G 47 107   087 W 57 127  103 g 67 147  119 w 77 167
072 H 48 110   088 X 58 130  104 h 68 150  120 x 78 170
073 I 49 111   089 Y 59 131  105 i 69 151  121 y 79 171
074 J 4a 112   090 Z 5a 132  106 j 6a 152  122 z 7a 172
075 K 4b 113   091 [ 5b 133  107 k 6b 153  123 { 7b 173
076 L 4c 114   092 \ 5c 134  108 l 6c 154  124 | 7c 174
077 M 4d 115   093 ] 5d 135  109 m 6d 155  125 } 7d 175
078 N 4e 116   094 ^ 5e 136  110 n 6e 156  126 ~ 7e 176
079 O 4f 117   095 _ 5f 137  111 o 6f 157  127  7f 177



128 Ä 80 200  144 ê 90 220  160 † a0 240  176 ∞ b0 260  192 ¿ c0 300  208 – d0 320   224 ‡ e0 340 240   f0 360
129 Å 81 201  145 ë 91 221  161 ° a1 241  177 ± b1 261  193 ¡ c1 301  209 — d1 321   225 · e1 341 241 Ò  f1 361
130 Ç 82 202  146 í 92 222  162 ¢ a2 242  178 ≤ b2 262  194 ¬ c2 302  210 “ d2 322   226 ‚ e2 342 242 Ú  f2 362
131 É 83 203  147 ì 93 223  163 £ a3 243  179 ≥ b3 263  195 √ c3 303  211 ” d3 323   227 „ e3 343 243 Û  f3 363
132 Ñ 84 204  148 î 94 224  164 § a4 244  180 ¥ b4 264  196 ƒ c4 304  212 ‘ d4 324   228 ‰ e4 344 244 Ù  f4 364
133 Ö 85 205  149 ï 95 225  165 • a5 245  181 µ b5 265  197 ≈ c5 305  213 ’ d5 325   229 Â e5 345 245 ı  f5 365
134 Ü 86 206  150 ñ 96 226  166 ¶ a6 246  182 ∂ b6 266  198 ∆ c6 306  214 ÷ d6 326   230 Ê e6 346 246 ˆ  f6 366
135 á 87 207  151 ó 97 227  167 ß a7 247  183 ∑ b7 267  199 « c7 307  215 ◊ d7 327   231 Á e7 347 247 ˜  f7 367
136 à 88 210  152 ò 98 230  168 ® a8 250  184 ∏ b8 270  200 » c8 310  216 ÿ d8 330   232 Ë e8 350 248 ¯  f8 370
137 â 89 211  153 ô 99 231  169 © a9 251  185 π b9 271  201 … c9 311  217 Ÿ d9 331   233 È e9 351 249 ˘  f9 371
138 ä 8a 212  154 ö 9a 232  170 ™ aa 252  186 ∫ ba 272  202   ca 312  218 ⁄ da 332   234 Í ea 352 250 ˙  fa 372
139 ã 8b 213  155 õ 9b 233  171 ´ ab 253  187 ª bb 273  203 À cb 313  219 € db 333   235 Î eb 353 251 ˚  fb 373
140 å 8c 214  156 ú 9c 234  172 ¨ ac 254  188 º bc 274  204 Ã cc 314  220 ‹ dc 334   236 Ï ec 354 252 ¸  fc 374
141 ç 8d 215  157 ù 9d 235  173 ≠ ad 255  189 Ω bd 275  205 Õ cd 315  221 › dd 335   237 Ì ed 355 253 ˝  fd 375
142 é 8e 216  158 û 9e 236  174 Æ ae 256  190 æ be 276  206 Œ ce 316  222 ﬁ de 336   238 Ó ee 356 254 ˛  fe 376
143 è 8f 217  159 ü 9f 237  175 Ø af 257  191 ø bf 277  207 œ cf 317  223 ﬂ df 337   239 Ô ef 357 255    ff 377


128 Ä      144 ê      160 †    176 ∞    192 ¿    208 –    224 ‡   240 
129 Å      145 ë      161 °    177 ±    193 ¡    209 —    225 ·   241 Ò
130 Ç      146 í      162 ¢    178 ≤    194 ¬    210 “    226 ‚   242 Ú
131 É      147 ì      163 £    179 ≥    195 √    211 ”    227 „   243 Û
132 Ñ      148 î      164 §    180 ¥    196 ƒ    212 ‘    228 ‰   244 Ù
133 Ö      149 ï      165 •    181 µ    197 ≈    213 ’    229 Â   245 ı
134 Ü      150 ñ      166 ¶    182 ∂    198 ∆    214 ÷    230 Ê   246 ˆ
135 á      151 ó      167 ß    183 ∑    199 «    215 ◊    231 Á   247 ˜
136 à      152 ò      168 ®    184 ∏    200 »    216 ÿ    232 Ë   248 ¯
137 â      153 ô      169 ©    185 π    201 …    217 Ÿ    233 È   249 ˘
138 ä      154 ö      170 ™    186 ∫    202      218 ⁄    234 Í   250 ˙
139 ã      155 õ      171 ´    187 ª    203 À    219 €    235 Î   251 ˚
140 å      156 ú      172 ¨    188 º    204 Ã    220 ‹    236 Ï   252 ¸
141 ç      157 ù      173 ≠    189 Ω    205 Õ    221 ›    237 Ì   253 ˝
142 é      158 û      174 Æ    190 æ    206 Œ    222 ﬁ    238 Ó   254 ˛
143 è      159 ü      175 Ø    191 ø    207 œ    223 ﬂ    239 Ô   255


 * RECORDS2.C illustrates reading and writing of file records with the
 * following functions:
 *      fgetpos     fsetpos
 *
 * See RECORDS1.C for a version using fseek, rewind, and ftell.
 *

#include <stdio.h>
#include <io.h>

 * File record  *
struct RECORD
{
    int     integer;
    long    doubleword;
    double  realnum;
} filerec = { 0, 1, 10000000.0 };

main()
{
    int c, newrec;
    size_t recsize = sizeof( filerec );
    FILE *recstream;
    fpos_t *recpos;

    / * Create and open temporary file. * /
    recstream = tmpfile();

    / * Write 10 unique records to file. * /
    for( c = 0; c < 10; c++ )
    {
	++filerec.integer;
	filerec.doubleword *= 3;
	filerec.realnum /= (c + 1);

	fwrite( &filerec, recsize, 1, recstream );
    }

    / * Find a specified record. * /
    do
    {
	printf( "Enter record betweeen 1 and 10 (or 0 to quit): " );
	scanf( "%d", &newrec );

	/ * Find and display valid records. * /
	if( (newrec >= 1) && (newrec <= 10) )
	{
	    *recpos = (fpos_t)((newrec - 1) * recsize);
	    fsetpos( recstream, recpos );
	    fread( &filerec, recsize, 1, recstream );

	    printf( "Integer:\t%d\n", filerec.integer );
	    printf( "Doubleword:\t%ld\n", filerec.doubleword );
	    printf( "Real number:\t%.2f\n", filerec.realnum );
	}
    } while( newrec );

    / * Starting at first record, scan each for specific value. * /
    *recpos = (fpos_t)0;
    fsetpos( recstream, recpos );
    do
    {
	fread( &filerec, recsize, 1, recstream );
    } while( filerec.doubleword < 1000L );

    fgetpos( recstream, recpos );
    printf( "\nFirst doubleword above 1000 is %ld in record %d\n",
	    filerec.doubleword, *recpos / recsize );

    / * Close and delete temporary file. * /
    rmtmp();
}



/ * RECORDS1.C illustrates reading and writing of file records using seek
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
 * /

#include <stdio.h>
#include <io.h>
#include <string.h>

/ * File record * /
struct RECORD
{
    int     integer;
    long    doubleword;
    double  realnum;
    char    string[15];
} filerec = { 0, 1, 10000000.0, "eel sees tar" };


main()
{
    int c, newrec;
    size_t recsize = sizeof( filerec );
    FILE *recstream;
    long recseek;

    / * Create and open temporary file. * /
    recstream = tmpfile();

    / * Write 10 unique records to file. * /
    for( c = 0; c < 10; c++ )
    {
	++filerec.integer;
	filerec.doubleword *= 3;
	filerec.realnum /= (c + 1);
	strrev( filerec.string );

	fwrite( &filerec, recsize, 1, recstream );
    }

    / * Find a specified record. * /
    do
    {
	printf( "Enter record betweeen 1 and 10 (or 0 to quit): " );
	scanf( "%d", &newrec );

	/ * Find and display valid records. * /
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

    / * Starting at first record, scan each for specific value. The following
     * line is equivalent to:
     *      fseek( recstream, 0L, SEEK_SET );
     * /
    rewind( recstream );

    do
    {
	fread( &filerec, recsize, 1, recstream );
    } while( filerec.doubleword < 1000L );

    recseek = ftell( recstream );
    / * Equivalent to: recseek = fseek( recstream, 0L, SEEK_CUR ); * /
    printf( "\nFirst doubleword above 1000 is %ld in record %d\n",
	    filerec.doubleword, recseek / recsize );

    / * Close and delete temporary file. * /
    rmtmp();
}



 * HEXDUMP.C illustrates directory splitting and character stream I/O.
 * Functions illustrated include:
 *      _splitpath      _makepath       getw            putw
 *      fgetc           fputc           fgetchar        fputchar
 *      getc            putc            getchar         putchar
 *
 * While fgetchar, getchar, fputchar, and putchar are not specifically
 * used in the example, they are equivalent to using fgetc or getc with
 * stdin, or to using fputc or putc with stdout. See FUNGET.C for another
 * example of fgetc and getc.
 *

#include <stdio.h>
#include <conio.h>
#include <io.h>
#include <dos.h>
#include <stdlib.h>
#include <string.h>

*/

void hex_main()
{

    int c,  newrec;
    size_t recsize = sizeof( filerec2 );
    FILE *recstream;

    FILE *infile, *outfile;
    char inpath[_MAX_PATH], outpath[_MAX_PATH];
    char drive[_MAX_DRIVE], dir[_MAX_DIR];
    char fname[_MAX_FNAME], ext[_MAX_EXT];
    int  in, size;
    long i = 0L;


    long recseek;

    /* Create and open temporary file. * /
    recstream = tmpfile();

    / * Write 10 unique records to file. * /
    for( c = 0; c < 10; c++ )
    {



	++filerec.integer;
	filerec.doubleword *= 3;
	filerec.realnum /= (c + 1);
	strrev( filerec.string );
	 * /

	fwrite( &filerec2, recsize, 1, outfile );
    }
    */


    /* Query for and open input file. */

    printf( "Enter input file name: " );
    gets( inpath );
    strcpy( outpath, inpath );

    if( (infile = fopen( inpath, "rb+" )) == NULL )
    {
	printf( "Can't open input file\n" );
	/*
	   nieuw file maken */
	printf("File is opened for writing \n");
	infile = fopen (inpath, "wb+");
	if (infile == NULL){
	   printf("Could not open file ");
	   getchar();
	   exit(1);
	}
    }

    /* Build output file by splitting path and rebuilding with
     * new extension.
     */
    _splitpath( outpath, drive, dir, fname, ext );
    strcpy( ext, "din" );  /* din */
    _makepath( outpath, drive, dir, fname, ext );

    /* If file does not exist, open it */
    if( access( outpath, 0 ) )
    {
	outfile = fopen( outpath, "wb+" );
	printf( "Creating %s from %s . . .\n", outpath, inpath );
    }
    else
    {
	printf( "Output file already exists" );

       /* exit( 1 ); */
    }

    /* Create and open temporary file. * /
	 recstream = tmpfile();
	 */
    /* Write 292 records to file. */

    for( c = 0; c < 292; c++ )
    {
	for (i=0; i<4; i++)
	     filerec2.lig[i]   = matrix[c].lig[i];
	filerec2.srt      = matrix[c].srt;
	filerec2.w        = matrix[c].w;
	filerec2.mrij     = matrix[c].mrij;
	filerec2.mkolom   = matrix[c].mkolom;
	/*
	printf( "String = %s  \n", filerec2.lig);
	printf( "width  = %d  \n", filerec2.w );
	printf( "srt    = %2d \n", filerec2.srt );
	printf( "row    = %2d \n", filerec2.mrij );
	printf( "column = %2d \n\n", filerec2.mkolom );
	if (getchar()=='#') exit(1);
	 */
	fwrite( &filerec2, recsize, 1, outfile );
    }


    rewind( outfile);
    recsize = sizeof( filerec2 );
    printf("Recsize = %4d ",recsize);
    if (getchar()=='#')exit(1);

    /* Find a specified record. */
    do
    {
	/*
	printf( "Enter record between 1 and 292 (or 0 to quit): " );
	scanf( "%d", &newrec );
	*/
	cls();
	printf("Nu de eerste 10 records : ");
	getchar();
	/* Find and display valid records. */
	for (newrec=1;newrec< 10;newrec++)
	     /* if( (newrec >= 1) && (newrec <= 292) ) */
	{

	    recseek = (long) ((newrec - 1) * recsize);
	    fseek( outfile, recseek, SEEK_SET );

	    fread( &filerec2, recsize, 1, outfile );


	    printf( "String = %s  \n", filerec2.lig);
	    printf( "width  = %d  \n", filerec2.w );
	    printf( "srt    = %2d \n", filerec2.srt );
	    printf( "row    = %2d \n", filerec2.mrij );
	    printf( "column = %2d \n\n", filerec2.mkolom );
	    if (getchar()=='#') exit(1);
	}
	if (getchar()=='#') exit(1);
	newrec=0;
    }
    while( newrec );

    printf("stoppen = # ");
    if (getchar()=='#') exit(1);




    /*





    */














    printf( "(B)yte or (W)ord: " );
    size = getche();

    /* Get each character from input and write to output. */
    while( 1 )
    {
	if( (size == 'W') || (size == 'w') )
	{
	    in = getw( infile );
	    if( (in == EOF) && (feof( infile ) || ferror( infile )) )
		break;
	    fprintf( outfile, " %.4X", in );
	    if( !(++i % 8) )
		putw( 0x0D0A, outfile );        /* New line      */
	}
	else
	{
	    /* This example uses the fgetc and fputc functions. You
	     * could also use the macro versions:
	    in = getc( infile );
	     */
	    in = fgetc( infile );
	    if( (in == EOF) && (feof( infile ) || ferror( infile )) )
		break;
	    fprintf( outfile, " %.2X", in );
	    if( !(++i % 16) )
	    {
		/* Macro version:
		putc( 13, outfile );
		 */
		fputc( 13, outfile );           /* New line      */
		fputc( 10, outfile );
	    }
	}
    }
    fclose( infile );
    fclose( outfile );
    exit( 0 );
}




