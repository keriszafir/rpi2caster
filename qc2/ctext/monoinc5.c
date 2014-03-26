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

typedef struct matrijs {
     char lig[4];  /* string present in mat
		      4 bytes: for unicode
		      otherwise 3 asc...
		      */
     unsigned char srt;      /* 0=romein 1=italic 2= kk 3=bold */
     unsigned char w;        /*

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
    unsigned char fixed;       /* fixed spaces 1/2 corps height */
    unsigned char right;       /* r_ight, l_eft, f_lat, c_entered */
    unsigned char ppp;         /* . . .
				3u + . 3 . 3 . 3.
				3u + !
				3u + ?
			       y/n */
};

typedef struct fspace {
    unsigned char pos;       /* row '_' space          */
    float         wsp;       /* width in point         */
    float         wunits;    /* width in units         */
    unsigned char u1;        /* u1 position 0075 wedge */
    unsigned char u2;        /* u2 position 0005 wedge */
    unsigned char code[12];  /* code fixed space       */
} ;


		/* used in verdeel() : */

unsigned char verdeelstring[VERDEEL];
       /* VERDEEL = 100... this number might be larger if needed */
unsigned char reverse[VERDEEL];
unsigned char revcode[4];


char tc[] = "ONMLKJIHGFsEDgCBA123456789abcdek";

unsigned char  tb[] = { 0x40, 0x20, 0x10, 0x08, 0x04, /* rowcode */
			0x02, 0x01, 0x80, 0x40, 0x20,
			0x10, 0x08, 0x04, 0x02, 0, 0 };

unsigned char  tk[] = { 0x42, 0x50, 0x80, 0x01,
			0x02, 0x80, 0x10, 0x40,
			0x80, 0x01, 0x02, 0x04,
			0x08, 0x10, 0x20, 0x40,
			0x80 };

char readbuffer [MAXBUFF];
long longbuffer [MAXBUFF];
char readbuffer2[MAXBUFF];
char readbuffer3[MAXBUFF];
int  nreadb2, nreadb3;
int  nreadbuffer;

unsigned char far cop[2000]; /* storage code during editing */
unsigned int  ncop;      /* number of bytes stored */


unsigned char ligk[15];  /* 0=roman, 1=italic, 2=small caps, 3=bold */
unsigned char ligl[15];  /* length of ligatures */
unsigned int  pcop[15];  /* pointers -> start code of a char in cop[] */
unsigned char npcop;     /* aantal pointers to cop[] */
unsigned char plrb[15];  /* pointer -> place in readbuffer */
long        fadres[15];  /* place in input file-txt   */
unsigned char nplrb;     /* number pointers -> plrb[] */

float    schuif[15];     /* tussen resultaten */
unsigned char nschuif;   /* aantal in schuif-register */

unsigned char o[2];      /* ontcijferen reverse$ */

/* all globals: concerning files:  */

FILE    *fintext;              /* pointer text file */
char    inpathtext[_MAX_PATH]; /* name text-file */
char    buffer[BUFSIZ];        /* buffer reading from text-file  */


FILE    *fouttext;            /* pointer text file */
char    outpathtext[_MAX_PATH]; /* name text-file */
char    outtextbuffer[BUFSIZ];        /* buffer reading from text-file  */



FILE     *foutcode;             /* pointer code file */
char     outpathcod[_MAX_PATH]; /* name cod-file     */
struct   monocode  coderec;     /* file record code file */

long     codepointer;            /* pointer in code file */
long int numbcode;               /* number of records in code-file */


FILE     *recstream;             /* pointer temporal file */
struct   monocode temprec;       /* filerecord temp-file  */
size_t   recsize = sizeof( temprec );
long     recseek;                /* pointer in temp-file */
long int codetemp = 0;           /* number of records in temp-file */

char drive[_MAX_DRIVE], dir[_MAX_DIR];
char fname[_MAX_FNAME], ext[_MAX_EXT];


unsigned char wig5[RIJAANTAL] =  /* 5 wedge */
     { 5,6,7,8,9, 9,9,10,10,11, 12,13,14,15,17, 18 };

unsigned char wig[RIJAANTAL] = {
		 5, 6, 7, 8, 9,
		 9, 9,10,10,11,
		12,13,14,15,18,18 }; /* 5 wedge */
		/*  5, 6, 7, 8, 9,
		 9,10,10,11,12,
		13,14,15,17,18,18 };
		 536 wedge ???? */




char namestr[34]; /* name font */
unsigned int nrows;

struct invoer_gens {
     char lll[4];
     unsigned char sys;  /* system */
     unsigned char spat; /* spatieeren 0,1,2,3 */
     unsigned char kol;  /* matrix[uitkomst].mkolom,    kolom 0-16  0 en 1 */
     unsigned char row;  /* matrix[uitkomst].mrij,      rij   0-15  12 */
     float ww;           /* matrix[uitkomst].w          width char  */
} invoer ;

int uitkomst;   /* global !!!! */




struct regel_data {
    float wsum;           /*  sum of widths already decoded chars
			    and fixed spaces
			   */
    float last;            /*  width left  margin  */
    float right;           /*  width right margin */
    float kind;
    unsigned char para;    /* paragraph on or off 0 = OFF, 1 = ON */
    unsigned char vs;      /* 0 = no white
			     >0 = add last white beginning line
			    */
    unsigned char rs;      /* number of lines with right margin */

    unsigned char addlines; /* add solid lines      */
    float    letteradd;   /* width to add to the char */
    unsigned char add;    /* add width to character x times */
    unsigned char nlig;   /* max length ligature */
    float former;         /*  width last line   */
    int   nspaces;        /*  number of variable spaces in the line */
    int   nfix;           /*  number of fixed spaces */
    int   curpos;         /*  place cursor in line */
    int   line_nr;        /*  number of chars on screen */
    char  linebuf1[200];
    char  linebuf2[200];
}   line_data,
    line_dat2 ;


struct gegevens central = { 50,   272, NORM2,    0, 'd',
			    12.0,
			    /* 30.,  24.,   */ 28.,
			    /*5.328, 4.2624,*/ 4.9728,
			    /* 552,  442,   */ 516,
			    'y','r','n' } ;
			    /* cochin 12 punt 12.25 maar gegoten op:
				12.5 wig...*/
struct gegevens centrl2;
unsigned char   kind = 0;  /* default roman */



struct fspace  datafix, datafix2 ;


unsigned char char_set = 45 ;      /* set garamond 12 pnt */

unsigned char cbuff[256]; /* storage code in gen_system */
unsigned char uitvul[2];  /* position adjustment wedges */

			 /* for fill_line */
int  qadd ;              /* = number of possible 9 spaces */
unsigned char var, left; /* = number variable spaces */


int      lnum ;  /* number of char in screen-strings */
unsigned char plaats[200];
unsigned char plkind[200];
float    maxbreedte;
int      t3j; /* teller in testzoek3 */

double aug, delta;

int spaties,
    esom ,
    eset = 50,
    idelta,
    itoe,
    qadd,
    radd,
    s1,s2,s3;
    unsigned char o[2];
    unsigned char var,left;
    double toe,toe2;

/* global data concerning matrix files */

int matmax = 272; /* fixed for now */
FILE  *finmatrix ;
struct matrijs matfilerec;
size_t mat_recsize = sizeof( matfilerec );
struct rec02 cdata;
size_t recs2       = sizeof( cdata  );
fpos_t *recpos, *fp;
int  mat_handle;
long int mat_length, mat_recseek;
char inpathmatrix[_MAX_PATH];
long int aantal_records; /* number of records in matrix-file */


