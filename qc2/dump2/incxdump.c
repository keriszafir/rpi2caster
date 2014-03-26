unsigned char     start;
unsigned char     vlag;
unsigned char    wvlag;

unsigned char     status;
unsigned char     stat1;
unsigned char     stat2;
unsigned char     stat3;

int p0075, p0005;
long pos;
int interf_aan ;

int gegoten;

float file_set;

unsigned iset;
float    set,inch,delta;


char answer;


int wedge[16] = {
    /*
    5, 6, 7, 8, 9,   9, 10, 10, 11, 12,   13, 14, 15, 17, 18, 18
    = 526 wig garamond
     */

    5,6,7,8,9, 9,9,10,10,11, 12,13,14,15,18,18 /* = 5 wedge */


    /*
    4,5,7,8,8 ,9,9,9,9,10, 11,12,12,13,15, 15  1331 wedge */

    };



/* File record */
struct RECORD
{
    int     integer;
    long    doubleword;
    double  realnum;
} filerec = { 0, 1, 10000000.0 };

/* File record */
struct RECORD1
{
    int     integer;
    long    doubleword;
    double  realnum;
    char    string[15];
} filerec1 = { 0, 1, 10000000.0, "eel sees tar" };

struct monorec
{
    unsigned char code[4];
    unsigned char separator;
}   mono;

char ontc[36];
int  ncode;
char mcode[20];
char caster;
char mcx[5];

int  coms;

unsigned char wig_05[4];
unsigned char wig_75[4];

unsigned char wig05[4] = { 0x00, 0x20, 0x00, 0x01 };
unsigned char wig75[4] = { 0x00, 0x24, 0x00, 0x00 } ;

unsigned char code[4];

unsigned char G1[4] = {0x00,0x80,0x40,0x00},
	      G2[4] = {0x00,0x80,0x20,0x00},
	      G5[4] = {0x00,0x80,0x04,0x00};



unsigned char GS1[4] = {0x00,0xa0,0x40,0x00},
	      GS2[4] = {0x00,0xa0,0x20,0x00},
	      GS5[4] = {0x00,0xa0,0x04,0x00};

unsigned char d11[4]; /* code for position 0075 wedge */

unsigned char d10[4]; /* code for position 0005 wedge */

unsigned char d11_10[4]; /*   */
unsigned char galley_out[4] = { 0x00, 0x24, 0x00,0x01} ;
	   /* code for line to galley */

unsigned char pump_on[4] = { 0x00, 0x24, 0x00,0x00};
	   /* code for pump on & 0075 wedge */
unsigned char pump_off[4] = { 0x0, 0x20, 0x0, 0x01 };


char csyst, uadding ;
int  syst;

char c[4];

void cls();


int p_atoi(int n );

long int pr;
int p_i, c_p;
int ps;

int p_atoi(int n )
{
    int teken;
    pr=0;
    teken = 1;
    ps=0;
    if (line_buffer[0]=='-') {
	teken = -1;
	ps++;
    }
    for (p_i=ps; p_i < n && p_i < (teken == 1) ? 4 : 5 ; p_i++) {

    /*    printf("pi=%3d b[i] = %3d ",p_i,line_buffer[p_i]);
	getchar(); */

	c_p=line_buffer[p_i];
	if (c_p >='0' && c_p<='9'){
	   pr*=10;
	   pr+=c_p-'0';
	/*   printf(" i= %3d c=%1c r=%5d ",p_i,c_p,pr);
	   if(getchar()=='#')exit(1); */
	} else break;

    }

    /*
    printf("eerste pr =%3d teken = %2d res = %8d ",pr,teken, pr*teken); getchar();
    if(getchar()=='#') exit(1);
     */

    return( teken * pr );
}

double p_atof(int n);

double r_pr, vm;

double p_atof(int n)
{
    double teken=1;

    r_pr=0;
    ps=0;
    for (ps=0; ps < n && line_buffer[ps] == 0; ps++);

    switch(line_buffer[ps]) {
       case '+' :
	   ps=1;
	   break;
       case '-' :
	   ps=1;
	   teken = -1.;
	   break;
    }

    for (p_i=ps; p_i < n; p_i++) {
       /*  printf("pi=%3d b[i] = %3d ",p_i,line_buffer[p_i]);
	   getchar(); */

	c_p=line_buffer[p_i];
	if (c_p >='0' && c_p<='9'){
	   r_pr *= 10.;
	   r_pr += (float) (c_p-'0');
	   /* printf(" i= %3d c=%1c r=%10.5f ",p_i,c_p,r_pr);
	   if(getchar()=='#')exit(1); */
	} else break;
    }
    if ( c_p == '.' || c_p == ',' ) {
	vm = 1; p_i++;
	for (   ; p_i < n; p_i++) {
	   /*
	   printf("pi=%3d b[i] = %3d ",p_i,line_buffer[p_i]);
	   getchar(); */
	   c_p=line_buffer[p_i];
	   if (c_p >='0' && c_p<='9'){
	      vm /= 10.;
	      r_pr += ((float) (c_p-'0')) * vm;
	    /*
	      printf(" i= %3d c=%1c r=%10.5f ",p_i,c_p,r_pr);
	      if(getchar()=='#')exit(1);
	      */
	   }
	   else break;
	}
    }

    return( r_pr * teken );
}

int ti,tj,tc;



void print_at( unsigned int r, unsigned int c, char x[] )
{
    int i;

    _settextposition( r, c );
    i=0;
    while (  x[i] != '\0' && i < 30 )
       putchar( x[i++]);

}


void setbit(int nr);

void setrow(int row);
void set_row( unsigned char s[4], int row );

void setcol(int col);

void f1();
void f2();

void seekmain();
void hexdump();
void ontcijfer();
void ontcijfer2();
void disp_bytes();

void delay2( int tijd );
void di_spcode();
void dispmono();

void control();

int  test_row();
int  test_NK();
int  test_NJ();
int  test2_NK(); /* werken met mcx[] */
int  test2_NJ();
int  test_O15();

int  test_N();
int  test_k();
int  test_g();
int  test_GS();

void zoekpoort();
void init();
void init_aan();
void init_uit();
void busy_uit();
void busy_aan();
void strobe_on ();
void strobe_out();
void strobes_out();

void gotoXY(int r, int k);
void noodstop();
void startinterface();
void zenden_codes();

unsigned char l[4];




void spaces()
{
    char kind, _cont, cc ;
    double sp_width; /* inchwidth space */
    double wigg;
    double delta_space;
    double w_sp;     /* width in points */
    int    number, i, w_i, spi ;
    int    ispace;
    int    row, column;
    int    spu1, spu2;
    int    try;

    cls();
    printf("Casting spaces at specified width \n\n");

    pump_on[0] = 0x00; 
    pump_on[1] = 0x24;
    pump_on[2] = 0; 
    pump_on[3] = 0;

    try =0;
    do {
       print_at(3,1,"             Set    = ");
       /* get_line(); */

       set = get__float(3,33 );

       iset = (int) (set * 4 + 0.5);
       set  = ( (float) iset ) *.25;

       printf("             Set    = %5.2f \n",set);
       try++;
       if (try > 5) {
	  getch();
	  do {
	     printf("Try = %1d ",try);
	     cc = getchar();
	     if (cc=='#') exit(1);
	     print_at(3,1,"             Set    = ");
	     /* get_line(); */

	     /* set = p_atof(get_line() ); */

	     set = get__float(3,33);

	     iset = (int) (set * 4 + 0.5);
	     set  = ( (float) iset ) *.25;
	     printf("             Set    = %5.2f \n",set);
	     getchar();
	  }
	     while (cc != '=');
	  set = 11.25;
	  try=0;
       }
    }
       while (set < 5. );

    do {
       print_at(6,1,"\n");
       printf("               pica = p \n");
       printf("              didot = d \n");
       printf("           fournier = f \n\n");
       printf("             system = ");
       while (! kbhit());
       kind = getch();
       if (kind == '#') exit(1);
    }
       while (kind != 'p' && kind != 'd' && kind != 'f' );
    /* dikte vragen */
    /* uitrekenen uitvulling */
    /* aantal vragen  */

    getchar();

    do {
       do {
	  cls();
	  print_at(3,1,"Width of the space in points ");

	  w_sp = get__float(13,33);

	  /*  w_sp = p_atof(get_line() ); */

	  w_sp += (w_sp < 0 ) ? -.25 : +.25;
	  w_sp *= 2.;
	  w_i = (int ) w_sp ;

	  w_sp = ( float) w_i;
	  w_sp *= .5;

	  switch ( kind ) {
	    case 'p' : printf("W_sp %8.3f points pica",w_sp); break;
	    case 'd' : printf("W_sp %8.3f points Didot",w_sp); break;
	    case 'f' : printf("W_sp %8.3f points fournier",w_sp); break;
	  }
	  printf(" getchar() ");

	  if (getchar()=='#')exit(1);
       }
	  while (w_sp < 2.  || w_sp > 14. );

       for(i=0;i<4;i++) mcx[i]=0;
       switch (kind ) { /* calculate correction */
	  case 'p' : /* 1 pica point = 1/12 * 1/6 = 1/72 inch */
	     sp_width = w_sp * .13888889 ;
	     break;
	  case 'd' : /* 12 didot point = .1776" 1 point .0148 */
	     sp_width = w_sp * .0148 ;
	     break;
	  case 'f' : /* 12 fournier point = 11 * .1776/12  "
			    1 point f = .013566666 */
	     sp_width = w_sp * .013566667;
	     break;
       }

       if ( w_sp < 3 ) {
	  row = 0;
	  for (i=0;i<4;i++) code[i]= GS1[i];
       } else {
	  if ( w_sp < 4 ) {
	      row = 1;
	      for (i=0;i<4;i++) code[i]= GS2[i];
	  } else {
	      if ( w_sp <11 ) {
		  for (i=0;i<4;i++) code[i]= GS5[i];
		  row = 4;
	      } else {
		  row = 15;
		  for (i=0;i<4;i++)code[i]=0;
		  code[1] = 0x20;  /* S */

	      }
	  }
       }
       wigg = wedge[row]*set/1296;
       delta_space = sp_width - wigg ;

       printf("row %2d units %2d \n",row+1, wedge[row]);
       printf("wedge  = %10.7f \n",wigg);
       printf("Space  = %10.7f \n",sp_width);
       printf("Delta  = %10.7f \n",delta_space);
       delta_space *= 2000;
       delta_space += (delta_space < 0) ? -.5 : .5;
       ispace = (int) delta_space;
       printf("Ispace = %4d ",ispace);

       spu1 = 1;
       spu2 = 38 + ispace;
       if (spu2 < 1 ) {
	     printf("Correction too small in spaces ");
	     getchar();
	     spu2 = 1;
       }
       if (spu2 > 226 ) {
	     printf("Correction to large in spaces ");
	     getchar();
	     spu2 = 226;
       }
       while (spu2 > 15) {
	     spu1++;
	     spu2 -= 15;
       }
       printf("Correction = %2d/%2d ",spu1,spu2);
       if (getchar()=='#') exit(1);

       do {
	  do {
	     cls();
	     print_at(5,1,"How many spaces to be cast   ");
	     number = get__int(5,33 );
	  }
	     while (number <= -1 );

	  if (number > 0 ) {
	     for (i=0;i<4;i++) mcx[i]=galley_out[i];
	     setrow(spu2);
	     f1();
	     if ( interf_aan ) zenden_codes();

	     for (i=0;i<4;i++) mcx[i]=pump_on[i];
	     setrow(spu1);
	     f1();
	     if ( interf_aan ) zenden_codes();


	     for ( spi=1; spi <= number; spi++) {

		for (i=0;i<4;i++) mcx[i]=code[i];
		f2();
		if ( interf_aan ) zenden_codes();

		if (spi % 15 == 0 ) {
		    for (i=0;i<4;i++) mcx[i]=galley_out[i];
		    setrow(spu2);
		    f2();
		    if ( interf_aan ) zenden_codes();

		    for (i=0;i<4;i++) mcx[i]=pump_on[i];
		    setrow(spu1);
		    f2();
		    if ( interf_aan ) zenden_codes();
		}
	     }

	     for (i=0;i<4;i++) mcx[i]=galley_out[i];
	     setrow(spu2);
	     f1();
	     if ( interf_aan ) zenden_codes();

	     for (i=0;i<4;i++) mcx[i]=pump_on[i];
	     setrow(spu1);
	     f1();
	     if ( interf_aan ) zenden_codes();

	  }
	  printf("end routine = e ");
	  _cont = getchar();
	  if ( _cont == '#') exit(1);

       }
	  while ( number > 0 );
       printf("end routine = e ");
       _cont = getchar();
       if ( _cont == '#') exit(1);

     }
       while ( _cont != 'e');
}

int read_width(int wig);

int read_width(int wig)
{

}

void apart()
{
    char cont ;
    char col[2] , row[2];
    unsigned b[4];
    int  /* rnr, cnr, */ wnr ;


    cls();

    caster = 'c';



    printf("casting seperate chars   \n\n");

    /*
       ask set

     */



    printf("now the separate character ");
    getchar();

    /*
    get_line();
    c[0]= line_buffer[0];
    c[1]= '\0'; / * line_buffer[1]; * /
     */


    rnr =    read_row(  );

    /* printf("rnr = %3d ",rnr); */

    cnr =    read_col();

    /* wnr =    read_width( wig ); */





    printf("Casting the chars : \n");

    printf("Put on the motor \n");
    getchar();
    for (tj=0;tj<4;tj++) mcx[tj]=0;
    mcx[1] |= 0x20;
    mcx[3]  = 0x81; /* pump off */

    f1();
    if ( interf_aan ) zenden_codes();
    if ( interf_aan ) zenden_codes();

    printf("put the pump-handle in ");
    getchar();

    for (tj=0;tj<4;tj++) mcx[tj]=0;
    mcx[1] = 0x24; /* 0075 =pump on */
    mcx[2] = 0x10;

    f1();
    if ( interf_aan ) zenden_codes();


    do
    {
       for (tj=0;tj<4;tj++) mcx[tj]=l[tj];
       for ( ti =0; ti < 20 ; ti++)
       {
	   f1();
	   if ( interf_aan )
	     zenden_codes();
       }

       mcx[1] = 0x24; /* S + 0075 */
       mcx[2] = 0x10; /* row 3 */
       mcx[3] = 0x81; /* 0005 => 8 position */

       f1();
       if ( interf_aan ) zenden_codes(); /* eject line */


       for (tj=0;tj<4;tj++) mcx[tj]=0;
       mcx[1] = 0x20; /* S */
       mcx[3] = 0x81; /* pump off */

       f1();
       if ( interf_aan ) zenden_codes();  /* pomp off */


       printf("take out character ");
       getchar();

       printf("ready ? <y/n> ");
       /* get_line(); */

       cont = getchar();

       if ( cont != 'y' )
       {
	  mcx[1] = 0x24;
	  mcx[3] = 0;
	  mcx[2] = 0x10; /* 0075 => position 3 */

	  f1();
	  if ( interf_aan ) zenden_codes();  /* switch on pump */
       }
    }
       while (cont != 'y');

}

void apart2()
{
    char cont, b_c ;
    char col[2] , row[2];
    unsigned b[4];
    int  i, rnr, cnr;

    cls();

    caster = 'c';



    printf("adjusting the diecase : at G8  \n\n");

    getchar();



    /* l[] */

    for (i=0;i<4;i++) l[i]=0;
    l[1]=0x80; /* ONML KJIH  GFSE DgCB  A123 4567  89ab cdek */

    l[3]=0x80; /* 0000 0000  1000 0000  0000 0000  1000 0000 */


    printf("Now the diecase at G8 : \n");

    printf("Put on the motor \n");
    getchar();
    for (tj=0;tj<4;tj++) mcx[tj]=0;
    mcx[1] = 0x20; /* S 8 k */
    mcx[3] = 0x81; /* pump off */

    f1();
    if ( interf_aan )
	 zenden_codes();
    if ( interf_aan )
	 zenden_codes();


    for (tj=0;tj<4;tj++) mcx[tj]=0;


    do
    {
       for (tj=0;tj<4;tj++) mcx[tj]=l[tj];  /* G8 */


       for ( ti =0; ti < 100 ; ) /* FOR EVER */
       {
	   f1();
	   if ( interf_aan )
	     zenden_codes();
	     if ( kbhit() ) {
		 b_c = getch();
		 if ( b_c=='#' /* || b_c==' ' */ ) {
		    /* printf("Busy uit -> noodstop \n");
		    noodstop();
		    exit(1);
		    */
		    break;
		 }
	     }

       }

       mcx[0] = 0x0; /* 0x4c; = njk */
       mcx[1] = 0x24; /* S 0075 */
       mcx[2] = 0x0;
       mcx[3] = 0x81; /* 0005 => 8 position */

       f1();
       if ( interf_aan ) zenden_codes();  /* eject line */
       f1();

       mcx[1] =0x20; /* S */

       if ( interf_aan ) zenden_codes();  /* pomp off */



       printf("take out character ");
       cont = getchar();
       printf("ready ? <y/n> ");
       get_line();
       cont = line_buffer[0];

       if ( cont != 'y' )
       {
	  /* mcx[0] = 0x48; */ /* NK */

	  mcx[1] = 0x24; /* S g */
	  mcx[3] = 0;
	  mcx[2] = 0x10; /* 0075 => position 3 */

	  f1();
	  if ( interf_aan ) zenden_codes();  /* switch on pump */
       }
    }
       while (cont != 'y');


}    /* c[ l[ */

void apart3()
{
    char cont ;
    char col[2] , row[2];
    unsigned char l1[4], l2[4];

    unsigned b[4];
    int  rnr, cnr,i;

    cls();

    caster = 'c';



    printf("adjusting low quad  \n\n");

    for (i=0; i<4 ; i++){
       l1[i]=0; l2[i]=0;
    }

    getchar();
    /*
    get_line();
    c[0]= line_buffer[0];
    c[1]= '\0';
     */

    /* ONML KJIH GFsEDgCB A1234567 89abcdek */

    l1[1]= 0x80; /* G */
    l2[0]= 0x01; /* H */
    l1[2]= 0x04; /* 5 */
    l2[2]= 0x04; /* 5 */



    printf("Now the chars : \n");

    printf("Put on the motor \n");
    getchar();
    for (tj=0;tj<4;tj++) mcx[tj]=0;

    /* mcx[0] = 0x44; */ /* NJ */
    mcx[1] = 0x20; /* S */
    mcx[3] = 0x81; /* pump off */
    f1();

    if ( interf_aan ) zenden_codes();
    if ( interf_aan ) zenden_codes();

    printf("put the pump-handle in ");
    getchar();


    for (tj=0;tj<4;tj++) mcx[tj]=0;


    /* mcx[0] = 0x48; */ /* NK */
    mcx[1] = 0x24; /* S g 0075 */
    mcx[2] = 0x10; /* 3  */

    f1();
    if ( interf_aan ) zenden_codes();


    do
    {
     for ( i=0; i< 6 ; i++) {
       for (tj=0;tj<4;tj++) mcx[tj]=l1[tj];
       f1();
       if ( interf_aan )
	     zenden_codes();

       for (tj=0;tj<4;tj++) mcx[tj]=l2[tj];
       f1();
       if ( interf_aan )
	     zenden_codes();

     }

      for (tj=0;tj<4;tj++) mcx[tj]=0;

      /* mcx[0] = 0x44; */ /* NJ */
      mcx[1] = 0x20; /* S */
      mcx[3] = 0x81; /* pump off */
      f1();
      if ( interf_aan ) zenden_codes();
      if ( interf_aan ) zenden_codes();

      printf("take out character ");
      cont = getchar();


       printf("ready ? <y/n> ");
       get_line();

       cont = line_buffer[0];

    }
       while (cont != 'y');


}
