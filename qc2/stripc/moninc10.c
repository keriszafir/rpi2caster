/* moninc10

   laatste versie marge ....


   void translate( unsigned char c, unsigned char com )
   void  calc_kg ( int n )
       adjust (int add, float add )
   void  store_kg( void )
   void  ontcijf( void )


   void  margin(  float length, unsigned char strt )
      fill_line ( units_last );
      keerom()
      translate( reverse[j] , com );

   void fill_line(  unsigned int u )
      void  calc_kg ( int n )
	 adjust (int add, float add )
      float adjust  ( int, float );
      void store_kg( void )
      int  iabsoluut( int )
      verdeel ( )

   lus in:

   #include <c:\qc2\stripc\monolus.c>

 */

/* variables margin */

int      mar_i, mar_j, mar_k, mar_nr;
float    mar_maxsub;
int      mar_subu, mar_units, mar_totunit;
char     mar_com;

/* variables fill_line     wsum */

int fill_i=0,  fill_n ;
unsigned char fill_casus;

/* variables translate */

int trns_i, trns_vt;

int end_line;

/* var lus : */

float lusl ;



int marge_i, marspc, mr_18, mr_s , m_i, m_rest;
float f_rest ;
float addition;

int mu1, mu2;
unsigned char u_1[4], u_2[4], u_S2[4]; mgs[4] ;
float mar_varsp;

void case_0();
void case_1();
void case_2();
void case_3();
void case_4();

void case_0()
{
	  /*         begin regel variabele spaties */


	  mr_s = mar_units / 6 ;
	  m_rest = mar_units % 6;
	  /*
	  printf(" marunits %4d mr_s = %4d m_rest %3d ",
		  mar_units, mr_s, m_rest );
	  if (getchar()=='#') exit(1);
	   */

	  mr_18 = 0;
	  while ( mr_s > mr_18+3 ) {
	     mr_18++;
	     mr_s  -= 3;
	  }

	  line_data.nspaces += mr_s;
	  /*
	  printf("18 = %2d vars %2d ",mr_18,mr_s);
	  printf(" line_data.nspaces = %3d ",line_data.nspaces);
	  if (getchar()=='#') exit(1);
	   */
	  if (line_data.nspaces > 0) {
	     mu1 = 0;           /* 2000/5184 */
	     mu2 = 53 + (int) (.5 +
		.385802469 * m_rest * central.set /
			 (float) line_data.nspaces  ) ;
	     while ( mu2  > 15 ){
		mu2 -= 15;
		mu1 ++;
	     }
	  }
	  else {
	     mu2 = 3;
	     mu1 = 8;
	     /*
	     printf("Nspaces = 0 ");
	     if (getchar()=='#') exit(1);
	      */
	  }
	  /*
	  printf("uitvulling %2d / %2d ",mu1,mu2);
	  if (getchar()=='#') exit(1);
	   */
	  setrow( u_1, mu1 );
	  setrow( u_2, mu2 );
	  setrow( u_S2, mu2);

	  while (mr_18 > 0 ) {
	     for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i] = 0;
	     store_code(); /* opslaan O-15 */
	     mr_18--;
	     for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i] = mgs[m_i];
	     store_code(); /* store var space */
	     mr_s--;
	  }

	  for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i]= mgs[m_i];
	  while ( mr_s > 0 ) {
	     /* opslaan spaties */
	     store_code();
	     mr_s --;
	  }

	  for ( m_i =0; m_i < 4; m_i++) {
	     cop[ncop++] = u_1[m_i]; /* opslaan */
	  }                          /* NK 0075 u_1 */
	  for ( m_i =0; m_i < 4; m_i++) {
	     cop[ncop++] = u_2[m_i]; /* opslaan */
	  }                          /* NKJ 0075 u_2 0005 => end line */

	  line_data.wsum = central.inchwidth;
;
}

void case_1()
{
		  /* @CR => line right alined
		   eind regel variable spaties */
	  /*
	  printf("Case 1 ");
	  getchar();
	   */
	  mr_s   = mar_units / 6 ;
	  m_rest = mar_units % 6;
	  /*
	  printf(" marunits %4d mr_s = %4d m_rest %3d ",
		  mar_units, mr_s, m_rest );
	  if (getchar()=='#') exit(1);
	   */
	  mr_18 = 0;
	  while ( mr_s > mr_18+3 ) {
	     mr_18++;
	     mr_s  -= 3;
	  }
	  /*
	  printf("18 = %2d vars %2d ",mr_18,mr_s);
	   */
	  line_data.nspaces += mr_s;
	  /*
	  printf(" line_data.nspaces = %3d ",line_data.nspaces);
	  if (getchar()=='#') exit(1);
	   */
	  if (line_data.nspaces >0) {

	     mu1 = 0;           /* 2000/5184 */
	     mu2 = 53 + (int) (.5 +
		.385802469 * m_rest * central.set/ (float) line_data.nspaces  ) ;
	     while ( mu2  > 15 ){
		mu2 -= 15;
		mu1 ++;
	     }
	  }
	  else {
	     mu2 = 3;
	     mu1 = 8;
	     /*
	     printf("Nspaces = 0 ");
	     if (getchar()=='#') exit(1);
	      */
	  }
	  /*
	  printf("uitvulling %2d / %2d ",mu1,mu2);
	  if (getchar()=='#') exit(1);
	   */
	  setrow( u_1, mu1 );
	  setrow( u_2, mu2 );
	  setrow( u_S2, mu2);

	  while (mr_s > mr_18 ) {
	     for (m_i=0; m_i<4; m_i++)
		cop[ncop++] = mgs[m_i]; /* opslaan GS2 */
	     mr_s --;
	     /*
	     printf("mr_s = %2d mr_18 = %2d ",mr_s,mr_18);
	     if (getchar()=='#') exit(1);
	      */
	  }
	  while (mr_18 > 0 ) {
	     for (m_i=0; m_i<4; m_i++)
		cop[ncop++] = mgs[m_i]; /* opslaan GS2 */
	     mr_s--;
	     for (m_i=0; m_i<4; m_i++)
		cop[ncop++] = 0 ; /* opslaan O-15 */
	     mr_18--;
	     /*
	     printf("mr_s = %2d mr_18 = %2d ",mr_s,mr_18);
	     if (getchar()=='#') exit(1);
	      */
	  }

	  for ( m_i =0; m_i < 4; m_i++) {
	     cop[ncop++] = u_1[m_i]; /* NK 0075 u1 */
	  }
	  for ( m_i =0; m_i < 4; m_i++) {
	     cop[ncop++] = u_2[m_i]; /* NKJ 0075 u2 0005 */
	  }

	  line_data.wsum = central.inchwidth;
;
}

int c_18, c_6;

void case_2()
{
	  mr_s = mar_units / 6 ;
	  m_rest = mar_units % 6;

	  if (mr_s % 2 == 1 ) {
	      mr_s --;
	      m_rest += 6;
	  }
	  mr_s /= 2;

	  mr_18 = 0;
	  while ( mr_s > mr_18+3 ) {
	     mr_18++;
	     mr_s  -= 3;
	  }
	  /*
	  printf("18 = 2* %2d vars 2* %2d ",mr_18,mr_s);
	   */

	  c_18= mr_18;
	  c_6= mr_s;


	  line_data.nspaces += 2 * mr_s;

	  /*
	  printf(" line_data.nspaces = %3d ",line_data.nspaces);
	  if (getchar()=='#') exit(1);
	   */

	  if ( line_data.nspaces> 0){
	     mu1 = 0;           /* 2000/5184 */
	     mu2 = 53 + (int) (.5 +
		.385802469 * m_rest * central.set/ (float) line_data.nspaces  ) ;
	     while ( mu2  > 15 ){
		mu2 -= 15;
		mu1 ++;
	     }
	  }
	  else {
	     mu2 = 3;
	     mu1 = 8;
	     /*
	      printf("Nspaces = 0 ");
	     if (getchar()=='#') exit(1);
	      */
	  }
	  /*
	  printf("uitvulling %2d / %2d ",mu1,mu2);
	  if (getchar()=='#') exit(1);
	   */


	  setrow( u_1, mu1 );
	  setrow( u_2, mu2 );
	  setrow( u_S2, mu2);


	  while (mr_18 > 0 ) {
	     for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i] = 0;
	     store_code(); /* opslaan O-15 */
	     mr_18--;
	     for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i] = mgs[m_i];
	     store_code(); /* store var space */
	     mr_s--;
	  }

	  for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i]= mgs[m_i];
	  while ( mr_s > 0 ) {
	     /* opslaan spaties */
	     store_code();
	     mr_s --;
	  }

	  /* nu achter cop plaatsen
	     eerst herstellen mr_18 en mr_s

	     */
	  mr_18 = c_18;
	  mr_s  = c_6;

	  while (mr_s > mr_18 ) {
	     for (m_i=0; m_i<4; m_i++)
		cop[ncop++] = mgs[m_i]; /* opslaan GS2 */
	     mr_s --;
	     /*
	     printf("mr_s = %2d mr_18 = %2d ",mr_s,mr_18);
	     if (getchar()=='#') exit(1);
	      */
	  }
	  while (mr_18 > 0 ) {
	     for (m_i=0; m_i<4; m_i++)
		cop[ncop++] = mgs[m_i]; /* opslaan GS2 */
	     mr_s--;
	     for (m_i=0; m_i<4; m_i++)
		cop[ncop++] = 0 ; /* opslaan O-15 */
	     mr_18--;
	     /*
	     printf("mr_s = %2d mr_18 = %2d ",mr_s,mr_18);
	     if (getchar()=='#') exit(1);
	      */
	  }


	  for ( m_i =0; m_i < 4; m_i++) {
	     cop[ncop++] = u_1[m_i]; /* NK 0075 u1 */
	  }
	  for ( m_i =0; m_i < 4; m_i++) {
	     cop[ncop++] = u_2[m_i]; /* NKJ 0075 u2 0005 */
	  }

	  line_data.wsum = central.inchwidth;

;
}
void case_3()
{
;
}
void case_4()
{
;
}


void  marge ( float length, unsigned char strt )
{
    /*
    print_at(1,6,"In marge ");
    printf("length = %12.4f strt = %3d \n",length, strt);
    printf("line-w   %12.4f \n",central.inchwidth);

    if (getchar()=='#') exit(1);
     */

    mar_units   = (int) (.5 + ( length * 5184. / (float) central.set ) );

    /*
    printf("length = %14.5f ",length);
    printf("in units %4d ",mar_units);
    if (getchar()=='#') exit(1);
     */

    mar_totunit += (int)
	( .5 + ( line_data.wsum * 5184. / (float) central.set ) );


    mr_18=0;
    mr_s =0;


    for (m_i=0; m_i<4; m_i++) {
	mgs[m_i]  = 0;
	u_1[m_i]  = 0;
	u_2[m_i]  = 0;
	u_S2[m_i] = 0;
    }

    mgs[1] = 0xa0; /* GS  */
    mgs[2] = 0x20; /*   2 */

    u_1[0] = 0x48; /* NK  */
    u_1[1] = 0x04; /* 0075 */

    u_2[0] = 0x4c; /* NKJ */
    u_2[1] = 0x04; /* 0075 */
    u_2[3] = 0x01; /* 0005 */

    u_S2[0] = 0x44; /* NJ */
    u_S2[3] = 0x01; /* 0005 */


    switch ( strt ) {
       case 0 : /* @CL => line left alined  */
	  case_0();
	  break;
       case 1 : /* @CR => line right alined */
	  case_1();
	  break;
       case 2 : /* @CC => line centered */
	  case_2();
	  break;
       case 3 : /* marge begin regel gedefineerde afstand */
	  /* kan naar cop hoeft echter niet
	       uitvulling berekenen naar mr_s
	       uitvulling telkens na de code tussenvoegen
	       ncop zal nog 0 zyn...

	       */


	  printf("Case 3 ");

	  mr_s   = mar_units / 6 ;
	  m_rest = mar_units % 6;

	  mr_18 = 0;
	  while ( mr_s > mr_18+3 ) {
	     mr_18++;
	     mr_s  -= 3;
	  }

	  printf("18 = %2d vars %2d ",mr_18,mr_s);

	  if (getchar()=='#') exit(1);



	  if ( mr_s > 0 ) {

	     mu1 = 0;           /* 2000/5184 */
	     mu2 = 53 + (int)
		(.5 + .385802469 * m_rest * central.set / (float) mr_s ) ;
	     while ( mu2  > 15 ){
		mu2 -= 15;
		mu1 ++;
	     }
	  }
	  else {
	     mu2 = 3;
	     mu1 = 8;
	     printf("mr_s = 0 ");
	     if (getchar()=='#') exit(1);
	  }
	  printf("uitvulling %2d / %2d ",mu1,mu2);
	  if (getchar()=='#') exit(1);

	  setrow( u_1, mu1 );
	  setrow( u_2, mu2 );
	  setrow( u_S2, mu2);

	  while (mr_18 > 0 ) {
	     for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i] = 0;
	     store_code(); /* opslaan O-15 */
	     mr_18--;
	     for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i] = mgs[m_i];
	     store_code(); /* store var space */
	     mr_s--;
	     for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i]= u_1[m_i];
	     store_code();
	     for ( m_i = 0;  m_i < 4; m_i++) mcx[m_i]= u_S2[m_i];
		  /* single justification for the var spaces*/
	     store_code();
	  }

	  while ( mr_s > 0 ) {
	     /* opslaan spaties */
	     for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i]= mgs[m_i];
	     store_code();
	     mr_s --;
	     for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i]= u_1[m_i];
	     store_code();
	     for ( m_i = 0;  m_i < 4; m_i++) mcx[m_i]= u_S2[m_i];
		  /* single justification for the var spaces*/
	     store_code();
	  }


	  line_data.wsum = length ;

	  break;
       case 4 : /* marge eind regel gedefineerde afstand */

	  /* naar cop
	       met

	       uitvulling berekenen naar mr_s
	       uitvulling telkens na de code tussenvoegen
	     1e stap: uitvullen regel hiervoor

	     line_data.nspaces ?



	     2e stap: uitvulling marge

		die doen we met vaste spaties

	     testen voor de aanroep:
		is line_data.wsum < central.inchwidth - length
		   EN line_data.nspaces == 0
		   dan aanroep als

		   marge ( central.inchwidth - line_data.wsum, 0 );

	  */





	  break;
       case 5 : /* vlak uitvullen als het kan */
	  if (line_data.nspaces > 0) {
	      f_rest = central.inchwidth - line_data.wsum;
	      addition = f_rest/ (float) line_data.nspaces;
	      printf("Addition = %12.5f ",addition);



	      if (addition  < 0.0935 ) {
		  /* 0.0935" is maximal addition to space */

		  mar_varsp = central.set < 48 ? 6. : 5. ;
		  mar_varsp = mar_varsp * (float) central.set / 5184;
		  mar_varsp += addition ;


		  printf("line width %12.5f \n", central.inchwidth);
		  printf("text width %12.5f \n", line_data.wsum);
		  printf("f_rest     %12.5f \n", f_rest);
		  printf("var spaces %3d ",line_data.nspaces);
		  printf("var wordt  %12.5f \n",mar_varsp);

		  if (getchar()=='#') exit(1);


		  mu1 = 0;
		  mu2 = 53;
		  mu2 += (int) (f_rest * 2000 + .5);

		  printf("mu2 = %3d ",mu2);
		  if (getchar()=='#') exit(1);


		  if ( mar_varsp < .156 ) {

		      while ( mu2  > 15 ){
			mu2 -= 15;
			mu1 ++;
		      }

		      printf("uitvulling %2d / %2d ",mu1,mu2);
		      if (getchar()=='#') exit(1);

		      setrow( u_1, mu1 );
		      setrow( u_2, mu2 );
		      for ( m_i =0; m_i < 4; m_i++) {
			cop[ncop++] = u_1[m_i]; /* NK 0075 u1 */
		      }
		      for ( m_i =0; m_i < 4; m_i++) {
			cop[ncop++] = u_2[m_i]; /* NKJ 0075 u2 0005 */
		      }
		      line_data.wsum = central.inchwidth;
		  }
		  else
		      case_1();
	      }
	      else
		  case_1();
	  }
	  else
	      case_1();

	  break;
    }

     /*
	dit snap ik geheel niet meer....

    if (central.set < 49 ) {
       mar_maxsub = (float) (line_data.nspaces * 2 * central.set);
    }  else {
       mar_maxsub = (float) (line_data.nspaces * central.set);
    }

    mar_maxsub /= 5184.;
    mar_subu = (int) (.5 + ( mar_maxsub * 5184. / (float) central.set ) );

      */

}


void bewaar_data()
{
    line_dat2.wsum       = line_data.wsum;
    line_dat2.last       = line_data.last;
    line_dat2.right      = line_data.right;
    line_dat2.kind       = line_data.kind;
    line_dat2.para       = line_data.para;
    line_dat2.vs         = line_data.vs;
    line_dat2.rs         = line_data.rs;
    line_dat2.addlines   = line_data.addlines;
    line_dat2.letteradd  = line_data.letteradd;
    line_dat2.add        = line_data.add;
    line_dat2.nlig       = line_data.nlig;
    line_dat2.former     = line_data.former;
    line_dat2.nspaces    = line_data.nspaces;
    line_dat2.nfix       = line_data.nfix;
    line_dat2.curpos     = line_data.curpos;
    line_dat2.line_nr    = line_data.line_nr;
}

void herstel_data()
{
    line_data.wsum  = line_dat2.wsum;
    line_data.last  = line_dat2.last;
    line_data.right = line_dat2.right;
    line_data.kind  = line_dat2.kind;
    line_data.para  = line_dat2.para;
    line_data.vs    = line_dat2.vs;
    line_data.rs    = line_dat2.rs;
    line_data.addlines  = line_dat2.addlines;
    line_data.letteradd = line_dat2.letteradd;
    line_data.add   = line_dat2.add;
    line_data.nlig  = line_dat2.nlig;
    line_data.former = line_dat2.former;
    line_data.nspaces = line_dat2.nspaces;
    line_data.nfix = line_dat2.nfix;
    line_data.curpos = line_dat2.curpos;
    line_data.line_nr = line_dat2.line_nr;
}


float lus_varsp;

#include <c:\qc2\stripc\monolus.c>




/*
   translate  reverse[] to monotype code
 */

void translate( unsigned char c, unsigned char com )
{
   for ( trns_i=0;trns_i<4;trns_i++) revcode[trns_i] = 0;

   switch ( c ) {
      case '#' : /* 015 = 0,0,0,0, */
	 break;
      case 'v' :
	 revcode[1] = 0xa0; /* GS  */
	 revcode[2] = 0x40; /*   1 */
	 break;
      case 'F' : /* fixed 9 unit space */
	 revcode[1] = 0x80; /* G   */
	 revcode[2] = 0x04; /*  5  */
	 break;
      case 'V' :
	 revcode[1] = 0xa0; /* GS  */
	 revcode[2] = 0x04; /*   5 */
	 break;
      default :
	 trns_vt = 0;
	 if ( c > '0' && c <= '9' ) {
	    trns_vt = c - '0';
	 }
	 if ( c >= 'a' && c <='f' ) {
	    trns_vt = c - 'a' + 10;
	 }
	 if (trns_vt > 0 ) {
	    switch ( com ) {
	       case '1':
		  revcode[0] = 0x48; /* NK  */
		  revcode[1] = 0x04; /*   g */
		  break;
	       case '2':
		  revcode[0] = 0x44; /* N J  */
		  revcode[3] = 0x01; /*    k */
		  break;
	       case 'a':
		  revcode[0] = 0x48; /* NK   */
		  revcode[1] = 0x04; /*   g  */
		  break;
	       case 'b':
		  revcode[0] = 0x4c; /* NKJ   */
		  revcode[1] = 0x04; /*    g  */
		  revcode[3] = 0x01; /*     k */
		  break;
	    }
	    revcode[2] |= rijcode[trns_vt-1][2];
	    revcode[3] |= rijcode[trns_vt-1][3];
	 }
	 break;
   }
}   /* translate */



/* #include <c:\qc2\stripc\monoin10.c> */

void calc_kg ( int n )
{
   adjust ( central.set < 48 ? wig[1] : wig[0] ,
	    ((float) idelta) /((float) n)
	   );
}

void store_kg( void )
{
   char c;

   verdeelstring[0] = (uitvul[1] <=9 ) ?
      ('0' + uitvul[1]) : ('a' - 10 + uitvul[1]);
   verdeelstring[1] = (uitvul[0] <=9 ) ?
      ('0' + uitvul[0]) : ('a' - 10 + uitvul[0]);
}


/*
   ontcijf = decipher first two byte of "verdeelstring"
*/

void  ontcijf( void )
{
   o[0] = ( verdeelstring[1] > '9') ?
	(verdeelstring[1] - 'a' + 10) : verdeelstring[1] - '0';
   o[1] = ( verdeelstring[0] > '9') ?
	(verdeelstring[0] - 'a' + 10) : verdeelstring[0] - '0';
}


/*
  keerom () : reverse verdeelstring[] => reverse[]

  in this order the code will be saved
*/

int krmi;
int krmn;

int keerom ( void )
{
   krmn=0;

   for ( krmi = 0; krmi < VERDEEL; krmi++)
      if (verdeelstring[ krmi ] != 0 ) krmn = krmi+1;
   for ( krmi = 0; krmi < krmn; krmi++)
      reverse[ krmi ]= verdeelstring[ krmn - krmi-1];
   reverse[ krmn ]='\0';

   return ( krmn );
}


/*
      void margin  ( float length, unsigned char strt )

      length in: inches

      lnum = number of codes stored already

      strt = 0: beginning line
      strt = 1: end of the line

      strt = 2: in the middle of a line

   version 29-02-2004
   version  3-03-2004
      added: possibility of empty lines
   version 12-03-2004
      all intern variables global

   version 8 september




      fill_line ( units_last );
      keerom()
      translate( reverse[j] , com );
 */

void  margin(  float length, unsigned char strt )
{
    char mc;

}


/*
     fill_line ( unsigned int u )

     version 2 feb 2004

     version 3 feb:
	built in the possibility of variable spaces and flat filled lines

     version 4 feb:
	verdeel$, combination fixed & variable spaces

     output in: verdeelstring[]

	V = GS5,   $[1]   / $[0] = position wedges
	v = GS1    $[n+1] / $[n] = position wedges
	f = G5
	# = O15

    uses functions:

    void fill_line(  unsigned int u )
	adjust ( int , float  );
	void  calc_kg ( int n )
    28 feb:   float adjust  ( int, float );
	void store_kg( void )
	int  iabsoluut( int )
	verdeel ( )

    12 maart: all variables global

*/

void fill_line(  unsigned int u )
{
      /*
      qadd = number of 9 unit spaces, that could fill the line
      var  = number of variable spaces used to fill out the line
       */
;
}  /* fill_line  */





