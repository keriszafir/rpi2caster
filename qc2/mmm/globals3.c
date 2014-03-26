  char    line_buffer[MAX_REGELS];
  char readbuffer [MAXBUFF];
  int  nreadbuffer;
  int  ntestbuf;
  int  crp_fread;
  long  filewijzer;
  int   EOF_f;

  typedef char regel[128];
  typedef struct monocode {
	unsigned char mcode[5];
    /*
	byte 0: O N M L   K J I H
	byte 1: G F S E   D g C B   g = '0075'
	byte 2: A 1 2 3   4 5 6 7
	byte 3: 8 9 a b   c d e k   k = '0005'
	byte 4: seperator byte
	      0xf0 = in file
	      0xff = eof-teken
     */
  } ;

  /* all globals: concerning files:  */
  FILE     *fintext;               /* pointer text file */
  char     inpathtext[_MAX_PATH];  /* name text-file */
  char     buffer[BUFSIZ];         /* buffer reading from text-file  */
  FILE     *fouttext;              /* pointer text file */
  char     outpathtext[_MAX_PATH]; /* name text-file */
  char     outtextbuffer[BUFSIZ];  /* buffer reading from text-file  */
  FILE     *foutcode;              /* pointer code file */
  char     outpathcod[_MAX_PATH];  /* name cod-file     */
  struct   monocode  coderec;      /* file record code file */
  long     codepointer;            /* pointer in code file */
  long int numbcode;               /* number of records in code-file */
  FILE     *recstream;             /* pointer temporal file */
  struct   monocode temprec;       /* filerecord temp-file  */
  size_t   recsize = sizeof( temprec );
  long     recseek;                /* pointer in temp-file */
  long int codetemp = 0;           /* number of records in temp-file */
  char drive[_MAX_DRIVE], dir[_MAX_DIR];
  char fname[_MAX_FNAME], ext[_MAX_EXT];

  unsigned char l[4];
  int    nlineb ;
  int    alpha;
  int    clri;
  int    lrj;
  int    lc1,lr1;
  int    lign;
  typedef struct matrijs {
     char lig[4];  /* string present in mat
		      4 bytes: for unicode
		      otherwise 3 asc...
		      */
     unsigned char srt;      /* 0=romein 1=italic 2= kk 3=bold */
     unsigned int  w;        /*

	      in a future version, this could be an int:
		   100 * 23 = 2300
	      calculations in 1/100 of an unit... is accurate enough
		 width in units  */

     unsigned char mrij  ;   /* place in mat-case   */
     unsigned char mkolom;   /* place in mat-case   */
  };
  typedef struct rec02 {
	     char cnaam[34];
    unsigned char wedge[RIJAANTAL];
    unsigned char corps[10];
    unsigned char csets[10];
  } ;
  typedef struct gegevens {
    unsigned char set ;     /* 4 times set                */
    unsigned int  matrices; /* total number of matrices   */
    unsigned char syst;     /* 0 = 15*15 NORM
			       1 = 17*15 NORM2
			       2 = 17*16 MNH
			       3 = 17*16 MNK
			       4 = 17*16 SHIFT
			       */
    unsigned char adding;      /* 0,1,2,3 >0 adding = on     */
    char          pica_cicero; /* p = pica,  d = didot  f = fournier  */
    float         corp;        /*  5 - 14 in points          */
    float         rwidth;      /* width in pica's/cicero     */
    float    inchwidth;        /* width in line in inches    */
    unsigned int  lwidth;      /* width of the line in units */
    unsigned char fixed;       /*  'n' / 'y' fixed spaces 1/2 corps height */
    unsigned char right;       /* r_ight, l_eft, f_lat, c_entered */

    unsigned char d_style;     /* dominant style */



    unsigned char ppp;         /* . . .
				3u + . 3 . 3 . 3.
				3u + !
				3u + ?
			       y/n
				*/
  };

  struct matrijs rd_mat;
  struct gegevens central = { 45,     /* set 11.25        47*/
			    272,    /* mats  15*17 = 255, 272 = 16*17  */
			    NORM2,
			    0,      /* nu unit adding  */
			    'd',    /* didot          */
			    12.0,   /* corps        */
   /* 20.,   16 width     */  24.,    /*   28.,      30.,    25.,    24.,    */
   /* 3.552, 2.8416 inch width*/   4.26,/*  4.9728,   5.328,  4.44,     4.2624,*/
   /*449.,  359.  units   */ 460.,    /* 629.,    674.,   561.,     539.,    */
			    'n',
			    'r',
			    '0', /* dominant style */
			    'n' } ;

  struct matrijs far matrix[ 340 ] =
     /* matmax 17*16 + 3*17 = 340  */

{

   "j"   ,1, 5, 0, 0,"l"   ,1, 5, 0, 1,"i"   ,1, 5, 0,02,"."   ,0,05, 0, 3,
   ","   ,0, 5, 0, 4,"\047",0, 5, 0, 5,"j"   ,0, 5, 0, 6,"i"   ,0, 5, 0, 7,
   " "   ,0, 5, 0, 8,"l"   ,0, 5, 0, 9,"("   ,0, 5, 0,10,"["   ,0, 5, 0,11,
   "."   ,3, 5, 0,12,","   ,3, 5, 0,13,""    ,0, 5, 0,14,""    ,0, 5, 0,15,
   "\047",3, 5, 0,16,
   "i"   ,2, 6, 1, 0,"\211",1, 6, 1, 1,"c"   ,1, 6, 1, 2,"s"   ,1, 6, 1, 3,
   "f"   ,1, 6, 1, 4,"t"   ,1, 6, 1, 5,"-"   ,0, 6, 1, 6,"f"   ,0, 6, 1, 7,
   " "   ,1, 6, 1, 8,"t"   ,0, 6, 1, 9,"e"   ,0, 6, 1,10,")"   ,0, 6, 1,11,
   "i"   ,3, 6, 1,12,"l"   ,3, 6, 1,13,"f"   ,3, 6, 1,14,"t"   ,3, 6, 1,15,
   "j"   ,3, 6, 1,16,
   "j"   ,2, 7, 2, 0,"s"   ,2, 7, 2, 1,"\224",1, 6, 2, 2,"v"   ,1, 7, 2, 3,
   "y"   ,1, 7, 2, 4,"g"   ,1, 7, 2, 5,"r"   ,1, 7, 2, 6,"o"   ,1, 6, 2, 7,
   "r"   ,0, 7, 2, 8,"s"   ,0, 7, 2, 9,"I"   ,0, 7, 2,10,":"   ,0, 5, 2,11,
   ";"   ,0, 5, 2,12,"!"   ,0, 5, 2,13,"r"   ,3, 7, 2,14,"I"   ,3, 7, 2,15,
   "-"   ,3, 7, 2,16,
   "p"   ,2, 8, 3, 0,"J"   ,1, 8, 3, 1,"I"   ,1, 8, 3, 2,"q"   ,1, 8, 3, 3,
   "b"   ,1, 8, 3, 4,"d"   ,1, 8, 3, 5,"h"   ,1, 8, 3, 6,"n"   ,1, 8, 3, 7,
   "a"   ,1, 8, 3, 8,"u"   ,1, 8, 3, 9,"a"   ,0, 8, 3,10,"e"   ,0, 8, 3,11,
   "c"   ,0, 8, 3,12,"z"   ,0, 8, 3,13,"\204",0, 8, 3,14,"\201",1, 8, 3,15,
   "\204",0, 8, 3,16,
   "y"   ,2, 9, 4, 0,"b"   ,2, 9, 4, 1,"l"   ,2, 9, 4, 2,"e"   ,2, 9, 4, 3,
   "?"   ,1, 9, 4, 4,"!"   ,1, 9, 4, 5,"ij"  ,1, 9, 4, 6,"p"   ,1, 9, 4, 7,
   " "   ,2, 9, 4, 8,"J"   ,0, 9, 4, 9,"3"   ,0, 9, 4,10,"6"   ,2, 9, 4,11,
   "9"   ,0, 9, 4,12,"5"   ,0, 9, 4,13,"8"   ,0, 9, 4,14,"a"   ,3, 9, 4,15,
   "z"   ,3, 9, 4,16,
   "z"   ,2, 9, 5, 0,"f"   ,2, 9, 5, 1,"t"   ,2, 9, 5, 2,"3"   ,3, 9, 5, 3,
   "fi"  ,1, 9, 5, 4,"fl"  ,1, 9, 5, 5,"z"   ,1, 9, 5, 6,"?"   ,0, 9, 5, 7,
   "x"   ,0, 9, 5, 8,"y"   ,0, 9, 5, 9,"7"   ,0, 9, 5,10,"4"   ,0, 9, 5,11,
   "1"   ,0, 9, 5,12,"0"   ,0, 9, 5,13,"2"   ,0, 9, 5,14,"e"   ,3, 9, 5,15,
   "c"   ,3, 9, 5,16,
   "x"   ,2,10, 6, 0,"q"   ,2,10, 6, 1,"u"   ,2,10, 6, 2,"o"   ,2,10, 6, 3,
   "S"   ,1,10, 6, 4,"k"   ,1,10, 6, 5,"q"   ,0,10, 6, 6,"h"   ,0,10, 6, 7,
   "p"   ,0,10, 6, 8,"g"   ,0,10, 6, 9,"ij"  ,0,10, 6,10,"b"   ,0,10, 6,11,
   "ff"  ,0,10, 6,12,"fl"  ,0,10, 6,13,"fi"  ,0,10, 6,14,"y"   ,3,10, 6,15,
   "S"   ,3,10, 6,16,
   "v"   ,2,10, 7, 0,"c"   ,2,10, 7, 1,"r"   ,2,10, 7, 2,"a"   ,2,10, 7, 3,
   "ff"  ,1,10, 7, 4,"S"   ,0,10, 7, 5,"v"   ,0,10, 7, 6,"k"   ,0,10, 7, 7,
   "u"   ,0,10, 7, 8,"n"   ,0,10, 7, 9,"o"   ,0,10, 7,10,"d"   ,0,10, 7,11,
   "\224",0,10, 7,12,"\201",0,10, 7,13,"o"   ,3,10, 7,14,"x"   ,3,10, 7,15,
   "v"   ,3,10, 7,16,

   "k"   ,2,11, 8, 0,"d"   ,2,11, 8, 1,"g"   ,2,11, 8, 2,"n"   ,2,11, 8, 3,
   "w"   ,1,11, 8, 4,"fi"  ,3,11, 8, 5,"fl"  ,3,11, 8, 6,"ff"  ,3,11, 8, 7,
   "u"   ,3,11, 8, 8,"n"   ,3,11, 8, 9,"ij"  ,3,11, 8,10,"g"   ,3,11, 8,11,
   "b"   ,3,11, 8,12,"d"   ,3,11, 8,13,"h"   ,3,11, 8,14,"k"   ,3,11, 8,15,
   "p"   ,3,11, 8,16,
   ""    ,0,12, 9, 0,""    ,0,12, 9, 1,"x"   ,1,12, 9, 2,"h"   ,2,12, 9, 3,
   "m"   ,2,12, 9, 4,"T"   ,1,12, 9, 5,"Z"   ,1,12, 9, 6,"B"   ,0,12, 9, 7,
   "C"   ,0,12, 9, 8,"L"   ,0,12, 9, 9,"F"   ,3,12, 9,10,"P"   ,3,12, 9,11,
   "F"   ,0,12, 9,12,"fb"  ,1,12, 9,13,"fh"  ,1,12, 9,14,"fk"  ,1,12, 9,15,
   "P"   ,0,12, 9,16,
   "Q"   ,1,13,10, 0,"Y"   ,1,13,10, 1,"K"   ,1,13,10, 2,"C"   ,1,13,10, 3,
   "L"   ,1,13,10, 4,"B"   ,1,13,10, 5,"P"   ,1,13,10, 6,"O"   ,1,13,10, 7,
   "m"   ,1,13,10, 8,"E"   ,0,13,10, 9,"T"   ,0,13,10,10,"R"   ,0,13,10,11,
   "Z"   ,0,13,10,12,"L"   ,3,13,10,13,"L"   ,3,13,10,14,"C"   ,3,13,10,15,
   "Z"   ,3,13,10,16,
   "w"   ,2,14,11, 0,"F"   ,1,14,11, 1,"R"   ,2,14,11, 2,"V"   ,0,14,11, 3,
   "Y"   ,0,14,11, 4,"A"   ,0,14,11, 5,"U"   ,0,14,11, 6,"w"   ,0,14,11, 7,
   "A"   ,2,14,11, 8,"E"   ,3,14,11, 9,"G"   ,3,14,11,10,"T"   ,3,14,11,11,
   "R"   ,2,14,11,12,"K"   ,3,14,11,13,"V"   ,3,14,11,14,"X"   ,3,14,11,15,
   "Y"   ,3,14,11,16,
   "G"   ,1,15,12, 0,"E"   ,1,15,12, 1,"U"   ,1,15,12, 2,"ffi" ,0,15,12, 3,
   "X"   ,0,15,12, 4,"K"   ,0,15,12, 5,"D"   ,0,15,12, 6,"G"   ,0,15,12, 7,
   "H"   ,0,15,12, 8,"N"   ,0,15,12, 9,"O"   ,0,15,12,10,"m"   ,0,15,12,11,
   "w"   ,3,15,12,12,"O"   ,3,15,12,13,"D"   ,3,15,12,14,"U"   ,3,15,12,15,
   "ffl" ,0,15,12,16,
   ""    ,0,17,13, 0,"Q"   ,0,17,13, 1,"V"   ,1,17,13, 2,"X"   ,1,17,13, 3,
   "D"   ,1,17,13, 4,"H"   ,1,17,13, 5,"N"   ,1,17,13, 6,"A"   ,1,17,13, 7,
   "M"   ,0,17,13, 8,"&"   ,0,17,13, 9,"m"   ,3,17,13,10,"ffi" ,3,17,13,11,
   "ffl" ,3,17,13,12,"H"   ,3,17,13,13,"N"   ,3,17,13,14,"&"   ,3,17,13,15,
   "Q"   ,3,17,13,16,
   ""    ,0,18,14, 0,"W"   ,1,18,14, 1,""    ,0,18,14,02,"M"   ,1,18,14, 3,
   "&"   ,1,18,14, 4,"W"   ,1,18,14, 5,"+"   ,0,18,14, 6,"M"   ,3,18,14, 7,
   "*"   ,0,18,14, 8,"W"   ,3,18,14, 9,"="   ,0,18,14,10,"---" ,3,18,14,11,
   "%"   ,0,18,14,12,"---" ,0,18,14,13,"..." ,0,18,14,14,".."  ,0,18,14,15,
   " "   ,4,18,14,16,
   ""    ,0,18,15, 0,""    ,0,18,15, 1,""    ,0,18,15,02,""    ,0,18,15, 3,
   ""    ,0,18,15, 4,""    ,0,18,15, 5,""    ,0,18,15, 6,""    ,0,18,15, 7,
   ""    ,0,18,15, 8,""    ,0,18,15, 9,""    ,0,18,15,10,""    ,0,18,15,11,
   ""    ,0,18,15,12,""    ,0,18,15,13,""    ,0,18,15,14,""    ,0,18,15,15,
   ""    ,0,18,15,16,
   ":"   ,2, 7, 2,14,";"   ,2, 7, 2,12,"!"   ,2, 7, 2,13,"?"   ,2, 9, 5, 7,
   "."   ,1, 5, 0, 3,"."   ,2, 5, 0, 3,","   ,2, 5, 0, 4,"\047",2, 5, 0, 5,
   "`"   ,2, 5, 0, 1,"-"   ,1, 6, 1, 6,"-"   ,2, 6, 1, 6,"--"  ,1, 9, 5,15,
   "--"  ,2, 9, 5,15,"---" ,1,18,14,12,"---" ,2,18,14,12,"\256",1, 9, 1,12,
   "\257",1, 9, 1,13,"\256",2, 9, 1,12,"\257",2, 9, 1,13,""    ,0,18,15, 0,
   ""    ,0,18,15, 1,""    ,0,18,15, 2,""    ,0,18,15, 3,""    ,0,18,15, 4,
   ""    ,0,18,15, 5,""    ,0,18,15, 6,""    ,0,18,15, 7,""    ,0,18,15, 8,


   ""    ,0,18,15, 9,""    ,0,18,15,10,""    ,0,18,15,11,""    ,0,18,15,12,
   ""    ,0,18,15,13,""    ,0,18,15,14,""    ,0,18,15,15,""    ,0,18,15,16,
   ""    ,0,18,15, 0,""    ,0,18,15, 1,""    ,0,18,15, 2,""    ,0,18,15, 3,
   ""    ,0,18,15, 4,""    ,0,18,15, 5,""    ,0,18,15, 6,""    ,0,18,15, 7,
   ""    ,0,18,15, 8,""    ,0,18,15, 9,""    ,0,18,15,10,""    ,0,18,15,11,

   ""    ,0,18,15,12,""    ,0,18,15,13,""    ,0,18,15,14,""    ,0,18,15,15,
   ""    ,0,18,15,16,""    ,0,18,15, 0,""    ,0,18,15, 1,""    ,0,18,15, 2,
   ""    ,0,18,15, 5,""    ,0,18,15, 4,""    ,0,18,15, 5,""    ,0,18,15, 6,
   ""    ,0,18,15, 9,""    ,0,18,15, 8,""    ,0,18,15, 9,""    ,0,18,15,10

   };

  unsigned char wig5[RIJAANTAL] =  /* 5 wedge */
     {      5,6,7,8,9,  9,9,10,10,11, 12,13,14,15,18 /* 17 ? */ , 18 };

  unsigned char wig[RIJAANTAL] = {
       /*   5,6,7,8,8,  9,9,10,10,11, 12,13,14,15,18,18 = 377 wedge */

	5,6,7,8,9, 9,10,10,11,12, 13,14,15,17,18,18  /* = 536 wedge */ };
	      /* 536 wedge */
  struct rec02 cdata;
  char   namestr[34];         /* name font */


   /*

   RECORDS1.C illustrates reading and writing of file records using seek
     functions including:
	  fseek       rewind      ftell

     Other general functions illustrated include:
	   tmpfile     rmtmp       fread       fwrite

     Also illustrated:
	  struct

     See RECORDS2.C for a version of this program using fgetpos and fsetpos.
     /
   #include <stdio.h>
   #include <io.h>
   #include <string.h>
   /   File record   /

   struct RECORD {
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

      /   Create and open temporary file.   /
      recstream = tmpfile();
      /   Write 10 unique records to file.   /
      for( c = 0; c < 10; c++ )
      {
	  ++filerec.integer;
	  filerec.doubleword *= 3;
	  filerec.realnum /= (c + 1);
	  strrev( filerec.string );
	  fwrite( &filerec, recsize, 1, recstream );
      }
      /   Find a specified record.   /
      do
      {
	  printf( "Enter record betweeen 1 and 10 (or 0 to quit): " );
	  scanf( "%d", &newrec );
	  /   Find and display valid records.   /
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
      /   Starting at first record, scan each for specific value. The following
	  line is equivalent to:
	       fseek( recstream, 0L, SEEK_SET );
	  /
      rewind( recstream );
      do
      {
	  fread( &filerec, recsize, 1, recstream );
      } while( filerec.doubleword < 1000L );
      recseek = ftell( recstream );
      /   Equivalent to: recseek = fseek( recstream, 0L, SEEK_CUR );   /
      printf( "\nFirst doubleword above 1000 is %ld in record %d\n",
	      filerec.doubleword, recseek / recsize );
      /   Close and delete temporary file.    /
      rmtmp();
   }




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



   */
