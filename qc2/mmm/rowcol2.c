#include <conio.h>
#include <stdio.h>
#include <graph.h>
#include <io.h>
#include <dos.h>
#include <stdlib.h>
#include <string.h>




#define  RIJAANTAL  16
#define  NORM       0
#define  NORM2      1
#define  MNH        2
#define  MNK        3
#define  SHIFT      4
#define  MAX_REGELS 55

#define  FALSE      0
#define  TRUE       1
#define  MAXBUFF    512
#define  HALFBUFF   256

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

struct matrijs far matrix[ 322 ];
     /* matmax 17*16 + 50 = 322  */

unsigned char wig5[RIJAANTAL] =  /* 5 wedge */
     { 5,6,7,8,9, 9,9,10,10,11, 12,13,14,15,18 /* 17 ? */ , 18 };

unsigned char wig[RIJAANTAL] = {
	  5,6,7,8,8, 9, 9,10,10,11, 12,13,14,15,18,18 /* = 377 wedge */

       /* 5,6,7,8,9, 9,10,10,11,12, 13,14,15,17,18,18  = 536 wedge */ };
	      /* 536 wedge */

struct rec02 cdata;
char   namestr[34];         /* name font */

void print_at(int r, int c, char *s);
void cls();
void introm();
void menu();


int get_line();
int test_EOF();
void a_b(int row, int col, int ibb );
void add_buf(int row,int col, int ibb, char c);
int  alphahex1 ( char c );
void clr_buf();
void r_mat ( int r );
int  get__row(int row, int co);
int  get__col( int row, int col);
void displaym();
void scherm3( void);
void scherm2();
void pri_coln(int column); /* prints column name */
void pri_lig( struct matrijs *m );
void read_mat( );
void read_inputname();
void disp_matttt(int nr);


void introm()
{;}


/* 18 mrt 2006 */

void disp_matttt(int nr)
{
    int dmi;

    printf("Matrix  %3d ",nr);
    printf("lig = ");
    for (dmi=0; dmi<3 ; dmi++)
	printf("%1c",matrix[nr].lig[dmi]);
    dmi = matrix[nr].lig[0];
    printf(" = %4d ", dmi );

    printf(" s = %1d ", matrix[nr].srt);
    printf(" w = %2d ", matrix[nr].w);
    printf(" r = %2d ", matrix[nr].mrij);
    printf(" c = %2d ", matrix[nr].mkolom);

    if (getchar() == '#') exit(1);
}


int gllimit;
int gli;
char glc;

int get_line()
{

   gllimit = MAX_REGELS;
   gli=0;
   while ( --gllimit > 0 && (glc=getchar()) != EOF && glc != '\n')
       line_buffer [gli++]=glc;
   if (glc == '\n')
       line_buffer[gli++] = glc;
   line_buffer[gli] = '\0';
   return ( gli );
}

int test_EOF()
{
    switch ( readbuffer[0] ) {
	 case '^' :
	 case '@' :
	    if ( readbuffer[1] == 'E' && readbuffer[2] == 'F'    )
		 EOF_f = 1 ;
	    break;
	 default :
	    EOF_f = 0;
    }

    return(EOF_f);
}



char mc;
int  stored;
int  fgelezen;

void menu()
{
    fgelezen = 0;
    stored = 0;

    do {
	cls();
	print_at( 4,10,"Editing Diecase-files");
	print_at( 6,10,"  new file   = n ");
	print_at( 6,10,"  read file  = r ");
	print_at( 7,10,"  store file = s ");
	print_at( 8,10,"  edit file  = e ");

	print_at(10,10,"  < stop = '#' > ");
	print_at(12,10,"  command = ");
	mc = getchar();
	switch(mc) {
	    case 'n' : /* new diecase     */
		       /* empty diecase   */
		       /* read all places */
	       break;
	    case 'd' : /* display file    */

	       break;
	    case 'r' : /* read file       */

	       break;
	    case 's' : /* store file      */

	       break;
	    case 'e' : /* edit file       */

	       break;
	}
    }
       while ( mc != '#');
}

int sts_try,fo;

void read_inputname()
{
    char tl;
    int ti;

    sts_try =0; fo = 0;
    do {
       do {
	  printf(" Enter file name:" );
	  tl = get_line();
	  for (ti=0;ti<tl-1; ti++)
	      inpathtext[ti]= line_buffer[ti];
       }
	  while (strlen(inpathtext) < 5);
       if( ( fintext = fopen( inpathtext, "rb" )) == NULL )
       {
	   printf("Open failure" );
	   sts_try ++;

	   if (  sts_try == 5 ) exit( 1 );
       }
       else
	   fo = 1;
    }
       while (! fo );
}


/*
    read_mat()

    added & tested 9 march 2006
    changed 10 march added: function convert();

    latest version 18 march 2006

 */

int regel_tootaal;  /* ??? */
int tst_i;

void read_mat( )
{
    char tc, *pc, ti, tl;
    int  ri, rj;
    int  firstline , crr ;
    char ans;
    int  recnr=0;


    for ( ri = 0; ri < 322 ; ri ++ ) {
	matrix[ ri ].lig[0] = '\0';
	matrix[ ri ].lig[1] = '\0';
	matrix[ ri ].lig[2] = '\0';
	matrix[ ri ].lig[3] = '\0';
	matrix[ ri ].srt = 0;
	matrix[ ri ].w = 0;
	matrix[ ri ].mrij = 0;
	matrix[ ri ].mkolom = 0;
    }

    firstline = 0;
    regel_tootaal = 0;

    /*
    clear_linedata();

    kind           = 0 ;
    line_data.last = 0.;
    line_data.vs   = 0 ;
    line_data.addlines = 0;
    line_data.add  = 0 ;
    line_data.nlig = 3 ;
    line_data.para = 0 ;
    line_data.c_style = 0;

    */
    /* default current style */

    /* line_data.dom */


    cls();

    for (tst_i=0; tst_i<
	  MAXBUFF;
	  tst_i++)
       readbuffer[tst_i] = '\0'; /* at the beginning this is empty */
    nreadbuffer = 0;
    ntestbuf = 0;

    inpathtext[0]='\0';
    inpathtext[1]='\0';

    cls();
    printf("Give name matrix file \n\n");
    read_inputname();
    crp_fread  = 0;
    filewijzer = 0;
    nreadbuffer=0;
    EOF_f = 0;
    do
    {
	crr = 0;
	if ( nreadbuffer > 3 ) {
	    if ( readbuffer[nreadbuffer-3] == '^' &&
		 readbuffer[nreadbuffer-2] == 'C' ) crr = 1;
	}
	if (crr == 0 ) leesregel();

	test_EOF();
	if ( EOF_f == 0 )
	{
	  /* disp_line(); */
	  for ( rj = 0; rj < nreadbuffer; rj +=18 ) {
	      switch ( readbuffer[rj] ) {
		 case '"' :
		    if (recnr < 322 ) {
		       matrix[ recnr ].mrij   =
			 convert ( readbuffer[rj+12] , readbuffer[rj+13] );
		       matrix[ recnr ].mkolom =
			 convert ( readbuffer[rj+15] , readbuffer[rj+16] ) ;
		       matrix[ recnr ].srt    = readbuffer[rj+7]-'0';
		       matrix[ recnr ].w      =
			 convert ( readbuffer[rj+ 9] , readbuffer[rj+10] ) ;
		       switch ( readbuffer[rj+1] ) {
			  case '\\':
			     matrix[ recnr ].lig[0] =
				( readbuffer[rj+2] - '0' ) * 64 +
				( readbuffer[rj+3] - '0' ) * 8 +
				( readbuffer[rj+4] - '0' ) ;
			     break;
			  case '"' :
			     break;
			  default :
			     matrix[ recnr ].lig[0] = readbuffer[rj+1];
			     if (readbuffer[rj+2] != '"') {
				matrix[ recnr ].lig[1] = readbuffer[rj+2];
				if (readbuffer[rj+3] != '"') {
				   matrix[recnr].lig[2] = readbuffer[rj+3];
				}
			     }
			     break;
		       }
		       disp_matttt(recnr);
		       recnr ++;
		    }
		    ri += 18;
		    break;
		 case '^' :
		 case '@' :
		    rj = nreadbuffer;
		    break;
	      }  /* switch */
	  } /* for loop */
	}
	for (rj =0; rj < nreadbuffer; rj++) readbuffer[rj] =  '\0';
	nreadbuffer = 0;
	if ( feof ( fintext) )  EOF_f = 1;
    }
	while ( EOF_f == 0 );
    fclose ( fintext);
}



void pri_lig( struct matrijs *m )
{
   print_at(4 + m -> mrij ,6+(m -> mkolom)*4,"    ");
   print_at(4 + m -> mrij ,6+(m -> mkolom)*4,"");
   switch ( m -> srt ) {
     case 0 : printf(" "); break;
     case 1 : printf("/"); break;
     case 2 : printf("."); break;
     case 3 : printf(":"); break;
   }
   printf("%1c%1c%1c",
      m -> lig[0],
      m -> lig[1],
      m -> lig[2] );
}



void pri_coln(int column) /* prints column name */
{
   switch (column) {
      case 0 : printf("NI");break;
      case 1 : printf("NL");break;
      default :
      printf(" %1c",63+column ); /* column A = 2 asc 65=A */
      break;
   }
}



/*
  scherm2 ()
    display skeleton on screen

    28-12-2003
*/
int nrows;
int scherm_i;

void scherm2()
{
    cls();

    for (scherm_i=0;scherm_i<=16;scherm_i++){
       print_at(3,7+scherm_i*4,"");
       pri_coln(scherm_i);
    }

    switch ( central.syst ) {
	case NORM  : nrows = RIJAANTAL-1 ; /* 15*15 */
	   break;
	case NORM2 : nrows = RIJAANTAL -1; /* 17*15 */
	   break;
	case SHIFT : nrows = RIJAANTAL;    /* 17*16 with Shift */
	   break;
	case MNH   : nrows = RIJAANTAL;    /* 17*16 with MNH */
	   break;
	case MNK   : nrows = RIJAANTAL;    /* 17*16 with MNK" */
	   break;

    }

    if (nrows > RIJAANTAL   ) nrows = RIJAANTAL;
    if (nrows < RIJAANTAL -1) nrows = RIJAANTAL -1;

    for ( scherm_i=0; scherm_i <= nrows-1; scherm_i++){

       print_at(scherm_i+4,1,"");  printf("%2d",scherm_i+1) ;
       print_at(scherm_i+4,78,""); printf("%2d",wig[scherm_i]);

       if (scherm_i > 18)  if (getchar()=='#') exit(1);
    }
}



void scherm3( void)
{

    print_at(20,10,"corps: ");
    for (scherm_i=0;scherm_i<10;scherm_i++) {
      if ( cdata.corps[scherm_i]>0 )  {
	 printf("%5.2f ", .5 * (double) cdata.corps[scherm_i] );
      }
	else
	 printf("      ");
    }
    print_at(21,10,"set  : ");
    for (scherm_i=0;scherm_i<10;scherm_i++) {
      if ( cdata.csets[scherm_i]>0 ) {
	 printf("%5.2f ", .25 * (double) cdata.csets[scherm_i] );
      }
       else
	 printf("      ");
    }
}


/*
   displaym: display the existing matrix

   28-12-2003

     scherm2();
     pri_lig( & mm );
     scherm3();


 */

int    dis_i ;
char   dis_c;
struct matrijs dis_mm;


void displaym()
{

    /*
      print_at(20,20," in displaym");
      printf("Maxm = %4d ",maxm);
      ontsnap("displaym");
     */

    scherm2();

    print_at(1,10," ");
    for (dis_i=0; dis_i<33 && ( (dis_c=namestr[dis_i]) != '\0') ; dis_i++)
	printf("%1c",dis_c);


    for (dis_i=0; dis_i< 272 ; dis_i++){
	 dis_mm = matrix[dis_i];
	 pri_lig( & dis_mm );
    }

    scherm3();

    print_at(24,10," einde display: ");
    getchar();

} /*  displaym() */




void print_at(int r, int c, char *s)
{
    _settextposition(r,c);
    _outtext( s );
}

void cls()
{
    _clearscreen( _GCLEARSCREEN );
}



int get__row(int row, int col)
{
    char c;
    int  u;

    print_at(row,col,"   ");
    _settextposition(row,col);

    do {
       while (!kbhit());
       c=getch();
       if (c==0) getch();
       if (c<'0' || c>'9') {
	   print_at(row,col," ");
	   print_at(row,col,"");
       }
    }
       while (c<'0' || c>'9');
    _settextposition(row,col);
    printf("%1c",c);

    line_buffer[nlineb++]=c;
    switch (c)
    {
       case '2' : u=1; l[2] |= 0x20; break;
       case '3' : u=2; l[2] |= 0x10; break;
       case '4' : u=3; l[2] |= 0x08; break;
       case '5' : u=4; l[2] |= 0x04; break;
       case '6' : u=5; l[2] |= 0x02; break;
       case '7' : u=6; l[2] |= 0x01; break;
       case '8' : u=7; l[3] |= 0x80; break;
       case '9' : u=8; l[3] |= 0x40; break;
       case '1' :
	  u=0;
	  print_at(row,col+1,"");
	  do {
	     while (!kbhit());
	     c=getche();
	     if (c!= 13 && c < '0' || c > '6' ) {
		print_at(row,col+1," ");
		print_at(row,col+1,"");
	     }
	  }
	     while (c!= 13 && c < '0' || c > '6' );
	  switch ( c) {
	     case 13 :
		l[2] |= 0x40;
		u = 0;
		line_buffer[nlineb++]='\0';
		break;
	     default :
		u = 9 + c - '0';
		line_buffer[nlineb++]=c;
		line_buffer[nlineb]='\0';
		switch (u) {
		   case  9 : l[3] |= 0x20; break;
		   case 10 : l[3] |= 0x10; break;
		   case 11 : l[3] |= 0x08; break;
		   case 12 : l[3] |= 0x04; break;
		   case 13 : l[3] |= 0x02; break;
		   case 14 : l[3] |= 0x00; break;
		}
		break;
	   }
	   break;
    }

    /*
    printf("u = %3d ",u);
    if (getchar()=='#') exit(1);
     */

    return (u);
}

int get__col(int row, int col)
{
    char c;
    int  u;

    print_at(row,col,"   ");
    _settextposition(row,col);

    do {
       while (!kbhit());
       c=getch();
       if (c==0) getch();

       if (c>='a' && c <='o') {
	   c += ('A' - 'a');
       }
       if (c<'A' || c>'0') {
	   print_at(row,col," ");
	   print_at(row,col,"");
       }
    }
       while (c<'A' || c>'O');
    _settextposition(row,col);
    printf("%1c",c);
    line_buffer[nlineb++]=c;
    switch (c)
    {
       case 'A' : u= 2; l[2] |= 0x80; break;
       case 'B' : u= 3; l[1] |= 0x01;break;
       case 'C' : u= 4; l[1] |= 0x02;break;
       case 'D' : u= 5; l[1] |= 0x08;break;
       case 'E' : u= 6; l[1] |= 0x10;break;
       case 'F' : u= 7; l[1] |= 0x40;break;
/* ONML KJIH  GFSE DgCB  A123 4567  89ab cdek */
       case 'G' : u= 8; l[1] |= 0x80;break;
       case 'H' : u= 9; l[0] |= 0x01;break;
       case 'I' : u=10; l[0] |= 0x02;break;
       case 'J' : u=11; l[0] |= 0x04;break;
       case 'K' : u=12; l[0] |= 0x08;break;
       case 'L' : u=13; l[0] |= 0x10;break;
       case 'M' : u=14; l[0] |= 0x20;break;

/* ONML KJIH  GFSE DgCB  A123 4567  89ab cdek */

       case 'O' : u=16; break;
       case 'N' :
	  _settextposition(row,col+1);
	  do {
	     while (!kbhit());
	     c=getche();
	     if ( c==0) getch();
	     if (c>='a' && c <='o') {
		  c += ('A' - 'a');
	     }

	     if (c!= 'I' && c!='L' && c != 13 ){
		print_at(row,col+1," ");
		_settextposition(row,col+1);
	     }
	  }
	     while (c!= 'I' && c!='L' && c != 13 );

	  _settextposition(row,col+1);
	  switch ( c) {
	     case 'I' :
		u = 0;
		l[0] |= 0x42; /* NI ONML KJIH */
		line_buffer[nlineb++]=c;
		line_buffer[nlineb]='\0';
		printf("%1c",c);

		break;
	     case 'L' :
		u = 1;
		l[0] |= 0x50; /* NL ONML KJIH */
		line_buffer[nlineb++]=c;
		line_buffer[nlineb]='\0';

		printf("%1c",c);
		break;
	     case 13 :
		u = 15;
		l[0] |= 0x40; /* N */
		line_buffer[nlineb]='\0';
		break;
	   }
	   break;
    }
    return(u);
}


void clr_buf()
{
   nlineb=0;
   for (clri=0;clri<20;clri++) line_buffer[clri]='\0';
}



void r_mat ( int r )
{
      print_at(r,1,"Read mat ");

      clr_buf();
      print_at(r,11,"Column ");
      lc1 = get__col(r,18 );
      line_buffer[nlineb++] ='-';
      printf(" row ");
      lr1 = get__row(r,25 );

      print_at(r,11,"                                     ");
      print_at(r,11,"");
      for (lrj=0; lrj < nlineb; lrj++)
	  printf("%1c",line_buffer[lrj]);

      clr_buf();
      print_at(r,15," = ");
     lign =  lig__get(r, 18);

}




void add_buf(int row,int col, int p, char c)
{
    _settextposition(row,col+nlineb);
    printf("%1c",c);
    line_buffer[nlineb++]= c;
}

void a_b(int row, int col,int p)
{
    _settextposition(row,col+nlineb-1);
    printf("%1c",line_buffer[nlineb-1]);
    line_buffer[nlineb--]='\0';

}


int alphahex1 ( char c )
{
   alpha = 0;

   if ( c >= '0' && c <= '9' ) alpha = c - '0';
   if ( c >= 'a' && c <= 'f' ) alpha = c - 'a' + 10;

   return ( alpha );
}

int lig__get(int row, int col)
{
    char c, c1, c2 ;
    int  nn;

    clr_buf();
    print_at(row,col,"               ");
    do {
       _settextposition(row,col+nlineb);
       while ( ! kbhit() );
       c=getch();
       if (c==0) {
	   getch();  /* ignore function keys */
       }
       c2 = 0 ;
       switch ( c ) {
	   case  0  :
	      c2 = - 1;
	      break;
	   case  8  :  /* backspace */
	      c2 = - 1;
	      if ( nlineb > 0 ) {
		 nlineb --;
		 line_buffer[nlineb]= '\0';
		 _settextposition(row,col+nlineb);
		 printf(" ");
		 _settextposition(row,col+nlineb);
	      }
	      break;
	   case '.' : case '?' : case '[' : case ':' : case '&' :
	   case ']' : case ';' : case '(' : case ')' : case '+' :
	   case '=' : case '*' : case '/' : case '@' : case '#' :
	   case '0' : case '1' : case '2' : case '3' : case '4' :
	   case '5' : case '6' : case '7' : case '8' : case '9' :
	   case '$' : case ' ' : case '%' : case '\\' :
	      /*
	      add_buf( row, col, nlineb,  c);
	      nlineb ++;
	       */
	      break;
	   case '-' :
	      if (nlineb > 0) {
		 switch (line_buffer[nlineb-1] ){
		     case 'd': /* 208 Ð d0 320 */
			line_buffer[nlineb-1]=0xd0;
			c2 =1; /* a_b( row, col, nlineb ); */
			break;
		     case 'D': /* 209 Ñ d1 321 */
			line_buffer[nlineb-1]=0xd1;
			c2 =1; /* a_b( row, col, nlineb ); */
			break;
		     default :
			/*
			add_buf( row, col, nlineb,  c);
			nlineb++;
			 */
			break;
		 }
	      }

	      break;
	   case '>' :
	      if (nlineb > 0) {
		 switch (line_buffer[nlineb-1] ){
		     case '>':
			line_buffer[nlineb-1]=0xae;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     default :
			/*
			add_buf( row, col, nlineb,  c);
			nlineb++;
			 */
			break;
		 }
	      }
	      break;
	   case '<' :
	      if (nlineb > 0) {
		 switch (line_buffer[nlineb-1] ){
		     case '<':
			line_buffer[nlineb-1]=0xaf;
			c2 =1; /* a_b( row, col, nlineb ); */
			break;
		     default :
			/*
			add_buf( row, col, nlineb,  c);
			nlineb++;
			 */
			break;
		 }
	      }

	      break;
	   case 'E' :
	      if (nlineb == 1 ) {
		 switch (line_buffer[nlineb-1] ){
		     case 'A':
			line_buffer[nlineb-1]=0x92;
			c2 = 1; /* a_b( row, col, nlineb ); */
			break;
		     default :
			/*
			add_buf( row, col, nlineb,  c);
			nlineb++;
			 */
			break;
		 }
	      }
	      break;
	   case 'e' :
	      if (nlineb == 1 ) {
		 switch (line_buffer[nlineb-1] ){
		     case 'a':
			line_buffer[nlineb-1]=0x91;
			c2 = 0; /* a_b( row, col, nlineb ); */
			break;
		     default :
			/*
			add_buf( row, col, nlineb,  c);
			nlineb++;
			 */
			break;
		 }
	      }
	      break;
	   case 'z' :
	      if (nlineb > 0) {
		 switch (line_buffer[nlineb-1] ){
		     case 's':
			line_buffer[nlineb-1]=0xe1;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     default :
			/*
			add_buf( row, col, nlineb,  c);
			nlineb++;
			 */
			break;
		 }
	      }
	      break;
	   case '!' :
	      if (nlineb > 0) {
		 switch (line_buffer[nlineb-1] ){
		     case 'c':
			line_buffer[nlineb-1]=0x87;
			c2 =1; /* a_b( row, col, nlineb );*/
			break;
		     case 'C':
			line_buffer[nlineb-1]=0x80;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     default :
			/*
			add_buf( row, col, nlineb,  c);
			nlineb++;
			 */
			break;
		 }
	      }
	      break;
	   case ',' :
	      if (nlineb > 0) {
		 switch (line_buffer[nlineb-1] ){
		     case 'c':
			line_buffer[nlineb-1]=0x87;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     case 'C':
			line_buffer[nlineb-1]=0x80;
			c2 = 1; /* a_b( row, col, nlineb ); */
			break;
		     default :
			/*
			add_buf( row, col, nlineb,  c);
			nlineb++;
			 */
			break;
		 }
	      }
	      break;
	   case '~' :
	      if ( nlineb > 0 ) {
		 switch (line_buffer[nlineb-1] ){
		     case 'n':
			line_buffer[nlineb-1]=0xa4;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     case 'N':
			line_buffer[nlineb-1]=0xa5;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     case 'a':
			line_buffer[nlineb-1]=0xc6;
			c2 =1; /* a_b( row, col, nlineb ); */
			break;
		     case 'A':
			line_buffer[nlineb-1]=0xc7;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     default :
			/*
			add_buf( row, col, nlineb,  c);
			nlineb++;
			 */
			break;
		 }
	      }
	      break;
	   case '"' :
	      if (nlineb > 0 ) {
		 switch (line_buffer[nlineb-1] ){
		     case 'a' :
			line_buffer[nlineb-1]=0x84;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     case 'e' :
			line_buffer[nlineb-1]=0x89;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     case 'i' :
			line_buffer[nlineb-1]=0x8b;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     case 'o' :
			line_buffer[nlineb-1]=0x94;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     case 'u' :
			line_buffer[nlineb-1]=0x81;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     case 'A' :
			line_buffer[nlineb-1]=0x8e;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     case 'E' :
			line_buffer[nlineb-1]=0xd3;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     case 'I' :
			line_buffer[nlineb-1]=0xd8;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     case 'O' :
			line_buffer[nlineb-1]=0x99;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     case 'U' :
			line_buffer[nlineb-1]=0x9a;
			c2=1; /* a_b( row, col, nlineb ); */
			break;
		     default :
			/*
			add_buf( row, col, nlineb,  c);
			nlineb++;
			 */
			break;
		 }
	      }
	      break ;
	   case '`' :
	      if (nlineb > 0 ) {
		 switch (line_buffer[nlineb-1] ){
		     case 'a' :
			line_buffer[nlineb-1]=0x85;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'e' :
			line_buffer[nlineb-1]=0x8a;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'i' :
			line_buffer[nlineb-1]=0x8d;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'o' :
			line_buffer[nlineb-1]=0x95;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'u' :
			line_buffer[nlineb-1]=0x97;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'A' :
			line_buffer[nlineb-1]=0xb7;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'E' :
			line_buffer[nlineb-1]=0xd4;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'I' :
			line_buffer[nlineb-1]=0xde;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'O' :
			line_buffer[nlineb-1]=0xe3;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'U' :
			line_buffer[nlineb-1]=0xeb;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     default :
			/*
			add_buf( row, col, nlineb,  c);
			nlineb++;
			 */

			break;
		 }
	      }
	      break ;
	   case '\'':
	      if (nlineb > 0 ) {
		 switch (line_buffer[nlineb-1] ){
		     case 'y' :
			line_buffer[nlineb-1]=0xec;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'Y' :
			line_buffer[nlineb-1]=0xed;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'a' :
			line_buffer[nlineb-1]=0xa0;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'e' :
			line_buffer[nlineb-1]=0x82;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'i' :
			line_buffer[nlineb-1]=0xa1;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'o' :
			line_buffer[nlineb-1]=0xa2;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'u' :
			line_buffer[nlineb-1]=0xa3;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'A' :
			line_buffer[nlineb-1]=0xb5;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'E' :
			line_buffer[nlineb-1]=0x90;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'I' :
			line_buffer[nlineb-1]=0xd6;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'O' :
			line_buffer[nlineb-1]=0xe0;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'U' :
			line_buffer[nlineb-1]=0xe9;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     default :
			/*
			add_buf( row, col, nlineb,  c);
			nlineb++;
			 */
			break;
		 }
	      }
	      break ;
	   case '^' :
	      if (nlineb > 0 ) {
		 switch (line_buffer[nlineb-1] ){
		     case 'a' :
			line_buffer[nlineb-1]=0x83;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'e' :
			line_buffer[nlineb-1]=0x88;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'i' :
			line_buffer[nlineb-1]=0x8c;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'o' :
			line_buffer[nlineb-1]=0x93;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'u' :
			line_buffer[nlineb-1]=0x96;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'A' :
			line_buffer[nlineb-1]=0xb6;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'E' :
			line_buffer[nlineb-1]=0xd2;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'I' :
			line_buffer[nlineb-1]=0xd7;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'O' :
			line_buffer[nlineb-1]=0xe2;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     case 'U' :
			line_buffer[nlineb-1]=0xea;
			c2=1; /* a_b( row, col, nlineb ); */break;
		     default :
			/*
			add_buf( row, col, nlineb,  c);
			nlineb++;
			 */
			break;
		 }
	      }
	      break ;
	   default :
	      if ( c >= 'a' && c <= 'z') {
		 /*
		 add_buf( row, col, nlineb,  c);
		 nlineb++;
		  */
	      } else {
		 if ( c >= 'A' && c <= 'Z') {
		    /*
		    add_buf( row, col, nlineb,  c);
		    nlineb++;
		     */
		 } else {
		    if (c !=13) {
		       c = 13;
		       c2 = -1;
		    }
		 }
	      }
	      break;
       }
       switch (c2 ) {
	   case 1 :
	      a_b( row, col, nlineb );
	      break;
	   case 0 :
	      add_buf( row, col, nlineb,  c);
	      break;
       }
    }
       while (nlineb < 4 && c != 13 );


    if (nlineb == 3 )
    {
       if ( line_buffer[1] == '/' )
       {
	  switch (line_buffer[0] )
	  {
	     case '3' :
	       if (line_buffer[2]=='4')
	       {
		    line_buffer[0] = 0xf3;
		    line_buffer[1] = 0;
		    line_buffer[2] = 0;
		    nlineb = 1;
		    _settextposition(row,col);
		    printf("%1c   ",line_buffer[0]);
	       }
	       break;
	     case '1' :
	       switch (line_buffer[2] )
	       {
		  case '2' :
		    line_buffer[0] = 0xab;
		    line_buffer[1] = 0;
		    line_buffer[2] = 0;
		    nlineb = 1;
		    _settextposition(row,col);
		    printf("%1c   ",line_buffer[0]);
		    break;
		 case '4' :
		    line_buffer[0] = 0xac;
		    line_buffer[1] = 0;
		    line_buffer[2] = 0;
		    nlineb = 1;
		    _settextposition(row,col);
		    printf("%1c   ",line_buffer[0]);
		    break;
	       }
	       break;
	  }
       } else {
	  if (line_buffer[0]=='^'){
	     c  = line_buffer[1];
	     c1 = line_buffer[2];
	     nn = 16 * alphahex1( c ) +alphahex1( c1 );
	     if ( nn >= 128 ) {
		 line_buffer[0] = nn;
		 line_buffer[1] = '\0';
		 line_buffer[2] = '\0';
		 nlineb = 1;
		 _settextposition(row,col);
		 printf("     ");
		 _settextposition(row,col);
		 printf("%1c   ",line_buffer[0]);
	     }
	  }
       }
    }
    line_buffer[nlineb]='\0';

    return (nlineb);
}



main()
{
   int i,j, n ;
   i=0;
   cls();
   do {
      r_mat(24);

      print_at(2,0,"                                           ");
      print_at(2,0,"");
      printf(" r1 = %2d c1 = %2d n= %2d lig = ",lr1,lc1,lign);
      for (j=0; j<lign; j++)
	 printf("%1c",line_buffer[j]);
      if ( getchar()=='#')exit(1);
      i++;
   }
      while (i<10);

   menu();
}



