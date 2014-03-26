
/*

       c:\qc2\last02\moninc10.c

   laatste versie marge ....








   void  margin(  float length, unsigned char strt )

      keerom()


   void fill_line(  unsigned int u )

      void  calc_kg ( int n )
	 adjust (int add, float add )
      float adjust  ( int, float );


      int  iabsoluut( int )


   lus in:

   #include <c:\qc2\stripc\monolus.c>

 */

/* variables marge */

int      mar_i, mar_j, mar_k, mar_nr;
float    mar_maxsub;
int      mar_subu, mar_units, mar_totunit;



/* variables fill_line     wsum */






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
		.385802469 * m_rest * central.cset /
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
		.385802469 * m_rest * central.cset/ (float) line_data.nspaces  ) ;
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
		.385802469 * m_rest * central.cset/ (float) line_data.nspaces  ) ;
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
/*
   0 = left alined
   1 = right alined
   2 = centered
   4 = margin at the beginning of the line
   5 = flat if possible
   6

 */

void  marge ( float length, unsigned char strt )
{
    /*
    print_at(1,6,"In marge ");
    printf("length = %12.4f strt = %3d \n",length, strt);
    printf("line-w   %12.4f \n",central.inchwidth);

    if (getchar()=='#') exit(1);
     */

    mar_units   = (int) (.5 + ( length * 5184. / (float) central.cset ) );

    /*
    printf("length = %14.5f ",length);
    printf("in units %4d ",mar_units);
    if (getchar()=='#') exit(1);
     */

    mar_totunit += (int)
	( .5 + ( line_data.wsum * 5184. / (float) central.cset ) );


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
		(.5 + .385802469 * m_rest * central.cset / (float) mr_s ) ;
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
	  printf("Case 5 \n");
	  if (line_data.nspaces > 0) {

	      f_rest = central.inchwidth - line_data.wsum;
	      addition = f_rest / (float) line_data.nspaces;

	      printf("Addition = %12.5f \n",addition);

	      if ( addition > -.0185) {


		  if (addition  < 0.0935 ) {

		     /* 0.0935" is maximal addition to space */

		     mar_varsp = central.cset < 48 ? 6. : 5. ;
		     mar_varsp = mar_varsp * (float) central.cset / 5184;
		     mar_varsp += addition ;

		     printf("line width %12.5f \n", central.inchwidth);
		     printf("text width %12.5f \n", line_data.wsum);
		     printf("f_rest     %12.5f \n", f_rest);
		     printf("var spaces %3d    \n",line_data.nspaces);
		     printf("var wordt  %12.5f \n",mar_varsp);

		     if (getchar()=='#') exit(1);

		     mu1 = 1;
		     mu2 = 38;
		     printf("add %15.5f \n",addition);
		     printf("bij %3d ",(int) (addition*2000. +.5) );

		     mu2 += (int) (addition * 2000. + .5);

		     printf("mu2 = %3d ",mu2);



		     while ( mu2  > 15 ){
			 mu2 -= 15;
			 mu1 ++;
		     }

		     printf("uitvulling %2d / %2d ### ",mu1,mu2);
		     if (getchar()=='#') exit(1);

		     setrow( u_1, mu1 );
		     for ( m_i =0; m_i < 4; m_i++) {
			 cop[ncop++] = u_1[m_i]; /* NK 0075 u1 */
		     }

		     setrow( u_2, mu2 );
		     for ( m_i =0; m_i < 4; m_i++) {
			    cop[ncop++] = u_2[m_i]; /* NKJ 0075 u2 0005 */
		     }
		     line_data.wsum = central.inchwidth;
		     if (getchar()=='#') exit(1);
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
    line_dat2.c_style    = line_data.c_style;


}

void herstel_data()
{
    line_data.wsum      = line_dat2.wsum;
    line_data.last      = line_dat2.last;
    line_data.right     = line_dat2.right;
    line_data.kind      = line_dat2.kind;
    line_data.para      = line_dat2.para;
    line_data.vs        = line_dat2.vs;
    line_data.rs        = line_dat2.rs;
    line_data.addlines  = line_dat2.addlines;
    line_data.letteradd = line_dat2.letteradd;
    line_data.add       = line_dat2.add;
    line_data.nlig      = line_dat2.nlig;
    line_data.former    = line_dat2.former;
    line_data.nspaces   = line_dat2.nspaces;
    line_data.nfix      = line_dat2.nfix;
    line_data.curpos    = line_dat2.curpos;
    line_data.line_nr   = line_dat2.line_nr;
    line_data.c_style   = line_dat2.c_style;
}


float lus_varsp;

/*
#include <c:\qc2\last02\monolus.c>
 */
















