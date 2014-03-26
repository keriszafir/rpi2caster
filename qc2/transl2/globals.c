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

   "\214",0, 5, 0, 0,"`"   ,0, 5, 0, 1,"i"   ,1, 5, 0,02,"."   ,0,05, 0, 3,
   ","   ,0, 5, 0, 4,"\047",0, 5, 0, 5,"j"   ,0, 5, 0, 6,"i"   ,0, 5, 0, 7,
   " "   ,0, 5, 0, 8,"l"   ,0, 5, 0, 9,"l"   ,1, 5, 0,10,""    ,0, 5, 0,11,
   "'"   ,1, 5, 0,12,","   ,1, 5, 0,13,"`"   ,1, 5, 0,14,"j"   ,1, 5, 0,15,
   "\214",1, 5, 0,16,
   "["   ,0, 5, 1, 0,"]"   ,0, 6, 1, 1,"c"   ,1, 6, 1, 2,
   "s"   ,1, 6, 1, 3,"f"   ,1, 6, 1, 4,"r"   ,1, 6, 1, 5,"-"   ,0, 6, 1, 6,
   "f"   ,0, 6, 1, 7," "   ,1, 6, 1, 8,"t"   ,0, 6, 1, 9,"e"   ,1, 6, 1,10,
   "("   ,0, 6, 1,11,")"   ,0, 6, 1,12,"\256",0, 9, 1,13,"\257",0, 9, 1,14,
   "\212",1, 6, 1,15,"\202",1, 6, 1,16,
   "j"   ,2, 6, 2, 0,"s"   ,2, 7, 2, 1,
   "\224",1, 6, 2, 2,"v"   ,1, 7, 2, 3,"y"   ,1, 7, 2, 4,"g"   ,1, 7, 2, 5,
   "r"   ,1, 7, 2, 6,"o"   ,1, 6, 2, 7,"r"   ,0, 7, 2, 8,"s"   ,0, 7, 2, 9,
   "I"   ,0, 7, 2,10,"\204",1, 7, 2,11,";"   ,0, 5, 2,12,"!"   ,0, 5, 2,13,
   ":"   ,0, 5, 2,14,":"   ,1, 7, 2,15,"\211",0, 8, 2,16,
   "p"   ,2, 8, 3, 0,
   "J"   ,1, 8, 3, 1,"I"   ,1, 8, 3, 2,"q"   ,1, 8, 3, 3,"b"   ,1, 8, 3, 4,
   "d"   ,1, 8, 3, 5,"h"   ,1, 8, 3, 6,"n"   ,1, 8, 3, 7,"a"   ,1, 8, 3, 8,
   "u"   ,1, 8, 3, 9,"a"   ,0, 8, 3,10,"e"   ,0, 8, 3,11,"c"   ,0, 8, 3,12,
   "z"   ,0, 8, 3,13,"\211",0, 8, 3,14,"\212",0, 8, 3,15,"\202",0, 8, 3,16,

   "y"   ,2, 9, 4, 0,"b"   ,2, 9, 4, 1,"6"   ,0, 9, 4, 2,"e"   ,2, 8, 4, 3,
   "?"   ,1, 9, 4, 4,"!"   ,1, 9, 4, 5,"ij"  ,1, 9, 4, 6,"p"   ,1, 9, 4, 7,
   ""    ,2, 9, 4, 8,"J"   ,0, 9, 4, 9,"3"   ,0, 9, 4,10,"l"   ,2, 9, 4,11,
   "9"   ,0, 9, 4,12,"5"   ,0, 9, 4,13,"8"   ,0, 9, 4,14,"\205",0, 9, 4,15,
   "\240",0, 9, 4,16,
   "t"   ,2, 9, 5, 0,"f"   ,2, 9, 5, 1,"4"   ,0, 9, 5, 2,
   "("   ,1, 9, 5, 3,"fi"  ,1, 9, 5, 4,"fl"  ,1, 9, 5, 5,"z"   ,1, 9, 5, 6,
   "?"   ,0, 9, 5, 7,"x"   ,0, 9, 5, 8,"y"   ,0, 9, 5, 9,"7"   ,0, 9, 5,10,
   "/"   ,0, 9, 5,11,"1"   ,0, 9, 5,12,"0"   ,0, 9, 5,13,"\204",0, 9, 5,14,

   "--"  ,0, 9, 5,15,"2"   ,0, 9, 5,16,

   ""    ,0,10, 6, 0,"z"   ,2,10, 6, 1,
   "u"   ,2,10, 6, 2,"o"   ,2,10, 6, 3,"S"   ,1,10, 6, 4,"k"   ,1,10, 6, 5,
   "q"   ,0,10, 6, 6,"h"   ,0,10, 6, 7,"p"   ,0,10, 6, 8,"g"   ,0,10, 6, 9,
   "ij"  ,0,10, 6,10,"b"   ,0,10, 6,11,"ff"  ,0,10, 6,12,"fl"  ,0,10, 6,13,
   "fi"  ,0,10, 6,14,"fj"  ,0,10, 6,15,"oe!" ,1,10, 6,16,

   ""    ,0,10, 7, 0,
   "q"   ,2,10, 7, 1,"r"   ,2,10, 7, 2,"a"   ,2,10, 7, 3,"ff"  ,1,10, 7, 4,
   "S"   ,0,10, 7, 5,"v"   ,0,10, 7, 6,"k"   ,0,10, 7, 7,"u"   ,0,10, 7, 8,
   "n"   ,0,10, 7, 9,"o"   ,0,10, 7,10,"d"   ,0,10, 7,11,"\224",0,10, 7,12,
   "\201",0,10, 7,13,"\341",0,10, 7,14,"\225",0,10, 7,15,"\242",0,10, 7,16,

   "n"   ,2,11, 8, 0,"x"   ,2,11, 8, 1,"v"   ,2,11, 8, 2,"c"   ,2,11, 8, 3,
   "w"   ,1,11, 8, 4,"x"   ,1,11, 8, 5,"F"   ,0,11, 8, 6,"P"   ,0,11, 8, 7,
   "k"   ,2,11, 8, 8,"d"   ,2,11, 8, 9,"g"   ,2,11, 8,10,"\226",0,11, 8,11,
   "\221",0,11, 8,12,"oe!" ,1,11, 8,13,"\243",0,11, 8,14,"\227",0,11, 8,15,
   ""    ,0,11, 8,16,

   ""    ,0,12, 9, 0,""    ,0,12, 9, 1,""    ,0,12, 9, 2,
   "h"   ,2,12, 9, 3,"m"   ,2,12, 9, 4,""    ,0,12, 9, 5,""    ,0,12, 9, 6,
   "B"   ,0,12, 9, 7,"C"   ,0,12, 9, 8,"L"   ,0,12, 9, 9,"L'"  ,0,12, 9,10,
   "st"  ,0,12, 9,11,"gy"  ,1,12, 9,12,"gg"  ,1,12, 9,13,"\200",0,12, 9,14,
   "st"  ,1,12, 9,15,""    ,1,12, 9,16,
   ""    ,0,13,10, 0,""    ,0,13,10, 1,
   "R"   ,0,13,10, 2,"T"   ,1,13,10, 3,"Z"   ,1,13,10, 4,"B"   ,1,13,10, 5,
   "P"   ,1,13,10, 6,"oe!" ,0,13,10, 7,"m"   ,1,13,10, 8,"E"   ,0,13,10, 9,
   "T"   ,0,13,10,10,"ffl" ,1,13,10,11,"Z"   ,0,13,10,12,"\200",1,13,10,13,
   "L'"  ,1,12,10,14,"ffi" ,1,13,10,15,""    ,1,13,10,16,

   ""    ,0,14,11, 0,
   "K"   ,1,13,11, 1,"w"   ,2,14,11, 2,"V"   ,0,14,11, 3,"Y"   ,0,13,11, 4,
   "A"   ,0,14,11, 5,"U"   ,0,14,11, 6,"w"   ,0,14,11, 7,"E"   ,1,14,11, 8,
   "Q"   ,1,14,11, 9,"Y"   ,1,14,11,10,"R"   ,1,14,11,11,"O"   ,1,14,11,12,
   "C"   ,1,13,11,13,"L"   ,1,13,11,14,"F"   ,1,14,11,15,""    ,0,14,11,16,

   "\222",1,15,12, 0,"OE!" ,1,15,12, 1,"m"   ,0,15,12, 2,"Q"   ,0,15,12, 3,
   "X"   ,0,15,12, 4,"K"   ,0,15,12, 5,"D"   ,0,15,12, 6,"G"   ,0,15,12, 7,
   "H"   ,0,15,12, 8,"N"   ,0,15,12, 9,"O"   ,0,15,12,10,"fk"  ,0,15,12,11,
   "G"   ,1,15,12,12,"U"   ,1,15,12,13,"fb"  ,0,15,12,14,"fh"  ,0,15,12,15,
   ""    ,0,15,12,16,

   ""    ,0,17,13, 0,""    ,0,17,13, 1,"V"   ,1,17,13, 2,
   "X"   ,1,17,13, 3,"D"   ,1,17,13, 4,"H"   ,1,17,13, 5,"N"   ,1,17,13, 6,
   "A"   ,1,17,13, 7,"M"   ,0,17,13, 8,"&"   ,0,17,13, 9,""    ,0,17,13,10,
   "ffl" ,0,17,13,11,"zy"  ,1,17,13,12,""    ,0,17,13,13,""    ,0,17,13,14,
   "ffi" ,0,17,13,15,""    ,0,17,13,16,

   ""    ,0,18,14, 0,"\222",0,18,14, 1,
   "OE!" ,0,18,14,02,"+"   ,0,18,14, 3,"*"   ,0,18,14, 4,"W"   ,1,18,14, 5,
   ""    ,0,18,14, 6,"W"   ,0,18,14, 7,"&"   ,1,18,14, 8,"@"   ,0,18,14, 9,
   "M"   ,0,18,14,10,"="   ,0,18,14,11,"---" ,0,18,14,12,"%"   ,0,18,14,13,
   "..." ,0,18,14,14,""    ,0,18,14,15," "   ,4,18,14,16,

   ""    ,0,18,15, 0,
   ""    ,0,18,15, 1,""    ,0,18,15,02,""    ,0,18,15, 3,""    ,0,18,15, 4,
   ""    ,0,18,15, 5,""    ,0,18,15, 6,""    ,0,18,15, 7,""    ,0,18,15, 8,
   ""    ,0,18,15, 9,""    ,0,18,15,10,""    ,0,18,15,11,""    ,0,18,15,12,
   ""    ,0,18,15,13,""    ,0,18,15,14,""    ,0,18,15,15,""    ,0,18,15,16,

   ":"   ,2, 7, 2,14,";"   ,2, 7, 2,12,"!"   ,2, 7, 2,13,"?"   ,2, 9, 5, 7,
   "."   ,1, 5, 0, 3,"."   ,2, 5, 0, 3,","   ,2, 5, 0, 4,"\047",2, 5, 0, 5,
   "`"   ,2, 5, 0, 1,"-"   ,1, 6, 1, 6,"-"   ,2, 6, 1, 6,"--"  ,1, 9, 5,15,
   "--"  ,2, 9, 5,15,"---" ,1,18,14,12,"---" ,2,18,14,12,"\256",2, 9, 1,12,
   "\257",2, 9, 1,13,"\256",1, 9, 1,12,"\257",1, 9, 1,13,""    ,0,18,15, 0,
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
     {      5,6,7,8,9,  9,9,10,10,11, 12,13,14,15,18   /* 17 ? */ , 18 };

  unsigned char wig[RIJAANTAL] = {

	    5,6,7,8,9,  9,9,10,10,11, 12,13,14,15,18,18 /* =  5-wedge  */
       /*   5,6,7,8,8,  9,9,10,10,11, 12,13,14,15,18,18 = 377 wedge */

       /* 5,6,7,8,9, 9,10,10,11,12, 13,14,15,17,18, 18  = 536 wedge */ };

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

   */
