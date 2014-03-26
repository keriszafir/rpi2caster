/* a:\transltr\monoinc8.c

   void  p_error( char *error )
   void  displaym()
      scherm2();
      pri_lig( & mm );
      scherm3();
   float adjust  (  unsigned char width, * units width row  *
		    float    add         * addition to char *
		  )
   int   i_abs( int a )
   int   zoek( char l[], unsigned char s, int max )

   void  dispmat(int max)
   float read_real ( void )
   void wis(int r, int k, int n)
   void tzint1()
   void tzint2( float maxbreedte )
   unsigned char  berek( char cy, unsigned char w )
   unsigned char  alphahex( char dig )
   void print_c_at( int rij, int kolom, char c)
   void clear_lined()
   void clear_linedata()



*/

void p_error( char *error )
{
   print_at(1,1,error);
   while ( ! kbhit () ) ;

   exit(1);
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


/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                                                                       *
 *     float adjust   (  width[row], float add )  27 feb 2004            *
 *                                                                       *
 *       limits to the adjusment of character:                           *
 *                                                                       *
 *      largest reduction : 1/1  2/7 = 35 * .0005" = .0185"              *
 *      neutral           : 3/8      = 0.000"                            *
 *      max addition      : 15/15 12/7 = 187 * .0005" = .0935"           *
 *                                                                       *
 *      The width of a character is not allowed to                       *
 *      exceed the witdh of the mat. standard mats: .2"*.2"              *
 *      Do not attempt to cast a character wider than .156" 312 *.0005"  *
 *      12 point character may a little bit wider.                       *
 *                                                                       *
 *      This gives an upper limit to the width a character can be cast   *
 *                                                                       *
 *      returns: the cast width                                          *
 *                                                                       *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

float   adj_t,  adj_tw;
int     adj_it, adj_itw, adj_itot;


float adjust  (  unsigned char width, /* units width row  */
		 float    add         /* addition to char */
	      )
{


   adj_t  = add * ( (float) central.set) / 5184.;
   adj_tw = ( ( float ) ( width * central.set) ) / 5184.;

   adj_it   = (int) ( adj_t  * 2000. + .5 ) ;
   adj_itw  = (int) ( adj_tw * 2000. + .5 ) ;

   adj_itot = adj_itw + adj_it;
   if ( central.set >= 48 )
   {
       if ( adj_itot  > 332 )   /* maximizing the addition */
	  adj_it = 332 - adj_itw;   /* according to table
		    justification wedge positions for adding
		    complete units
		 */
   } else {
       if ( adj_itot > 312 )
	  adj_it = 312 - adj_itw;
   }
   adj_it += 53;               /* 3/8 is neutral */
   if (adj_it <  16) adj_it = 16;
	  /* minimum  1/1  = 3/8 -  2/7 = -.0185" */
   if (adj_it > 240) adj_it = 240;
	  /* minimum 15/15 = 3/8 + 12/7 = +.0935" */
   if ( ( adj_it % 15) == 0){
       uitvul[1] = 15;
       uitvul[0] = (adj_it / 15) -1;
   } else {
       uitvul[1] = adj_it % 15;
       uitvul[0] = adj_it / 15;
   }

   return ( adj_tw + ( ( float) adj_it) / 2000. );
} /* adjust */


/*
      seeks the place of a ligature in the matcase

      liniair search routine, no tables...
      keeping it simple

      24-1-2004: was unsigned char => int
      the mat-case can contain 17*16 mats, and
      the font a lot more 272

*/

int zoek_rci;
int zoek_rcnr;
int zoek_rcgevonden ;
int zoek_rcsum;
char zoek_rcc;
unsigned char zoek_rcst;
unsigned char zoek_rclen;

int      i_abs( int a )
{
   return ( a < 0 ? -a : a );
}

int zoek( char l[], unsigned char s, int max )
{

   zoek_rcgevonden = FALSE;
   zoek_rcnr=-1;
   zoek_rcsum = 0;
   zoek_rcst = s;

   /*
   printf("in zoek: l = %1c %1c %1c s = %1d ",l[0],l[1],l[2],s); if (getchar()=='#')exit(1);
    */

   if ( zoek_rcst == 2) {   /* only lower case will be small caps */
      if (  (l[0] < 97) || (l[0] > 122) ){
	  zoek_rcst = 0;
      }
   }

	       /* italic/small cap point as roman point */
   zoek_rclen = 0;
   for (zoek_rci=0; zoek_rci<4 && l[zoek_rci] != '\0'; zoek_rci++)
   {  /* determine length l[] */
       if (l[zoek_rci] != '\0') zoek_rclen++;
   }
   if (zoek_rclen == 1)   /* for now: no italic or small-cap points */
   {
      switch (l[1])
      {
	 case '.' :
	   if (zoek_rcst != 3) zoek_rcst = 0;
	   break;
	 case '-' :
	   if (zoek_rcst != 3) zoek_rcst = 0;
	   break;
      }
   }


   do {
      zoek_rcnr ++;
      zoek_rcsum = 0;
		 /* unicode => 4 */
      for (zoek_rci=0, zoek_rcc=l[0] ;
		 zoek_rci< 3 && zoek_rcc != '\0' ;
			      zoek_rci++) {
	      /* printf("l[%1d] = %3d m.lig[] = %3d ",zoek_rci,l[zoek_rci],
			      matrix[zoek_rcnr].lig[zoek_rci]);
	       */
	   zoek_rcsum += i_abs( l[zoek_rci]
			     - matrix[zoek_rcnr].lig[zoek_rci] );
	   /* printf("sum = %4d \n",zoek_rcsum); */
      }


      /* if (zoek_rcsum < 10 ) {
	      printf("Sum = %6d nr = %4d ",zoek_rcsum,zoek_rcnr);
	      printf("m %1c %1c %1c sm = %1d ",
		      matrix[zoek_rcnr].lig[0],
		      matrix[zoek_rcnr].lig[1],
		      matrix[zoek_rcnr].lig[2],
		      matrix[zoek_rcnr].srt );
	      ce();

       } */


      zoek_rcgevonden = ( (zoek_rcsum == 0 ) &&
		  ( matrix[zoek_rcnr].srt == zoek_rcst ) ) ;

      if (zoek_rcnr > 450) exit(1);
   }
      while ( (zoek_rcgevonden == FALSE) && ( zoek_rcnr < max - 1 ) );
       /* printf("Na de lus "); ce(); */

   if (zoek_rcgevonden == TRUE){
      return ( zoek_rcnr );
   } else
      return ( -1 );
}
/* zoek */

int dspmti;
int dspmtj;

void dispmat(int max)

{

   for (dspmti=0; dspmti <max; dspmti++){
      printf(" lig      = ");
      for (dspmtj=0; dspmtj<3 ; dspmtj++)
	       /* unicode => 4 */
	  printf("%c",matrix[ dspmti].lig[dspmtj] );
      printf(" soort    = %3d ",matrix[dspmti].srt);
      printf(" breedte  = %3d ",matrix[dspmti].w);
      printf(" rij      = %3d ",matrix[dspmti].mrij);
      printf(" kolom    = %3d ",matrix[dspmti].mkolom);

      if ('#'==getchar() ) dspmti = max;
   }
}


float read_real ( void )
{
    get_line ();
    return (atof(line_buffer));
}

int wis_i;
int wis_n2;

void wis(int r, int k, int n)
{
     wis_n2 = n;
     while ( k + wis_n2 > 79) wis_n2--;

     for (wis_i=0;wis_i<=wis_n2;wis_i++)
	 print_c_at( r, k + wis_i,' ');
}

void tzint1()
{
    cls();
    printf("tzint1 : gegevens ");
    printf("set       %4d\n",  central.set);
    printf("matrijzen %4d\n",  central.matrices);
    printf("syst      %4d\n",  central.syst);
    printf("adding    %4d\n",  central.adding);
    printf("pica_cic  %1c\n",central.pica_cicero);
    printf("linewidth %4d\n",  central.lwidth);
    ce();
}


void tzint2( float maxbreedte )
{
   print_at(23,1,"tzint2: marge ");
   printf("%7.5f ncop %3d", line_data.wsum, ncop );
   printf("maxb %7.5f line %7.5f c %1c",
	  maxbreedte, central.inchwidth, readbuffer[0] );

   print_at(24,1,"");
   printf( line_data.wsum < maxbreedte ? "<<" : ">>");
   if ('#'==getchar()) exit(1);

}

unsigned char brk_add;

unsigned char  berek( char cy, unsigned char w )
{

   brk_add = alphahex( cy );

   while  ( (line_data.wsum + brk_add * w ) > central.lwidth)
	       brk_add --;

   return( brk_add );
}


unsigned char alpha_add;

unsigned char  alphahex( char dig )
{
   alpha_add = 0;

   if ( dig >= 'A' && dig <='F' ) dig +=  ('a'-'A');

   if ( (( dig > '0') && ( dig <= '9')) ||
	(( dig >='a') && ( dig <= 'f'))  )
   {
	alpha_add = ( dig <= '9' ) ?  dig - '0' :  dig - 'a' + 10;
   }
	else  alpha_add = 0;

   return( alpha_add );
}


void print_c_at( int rij, int kolom, char c)
{
    _settextposition( rij , kolom );
    printf("%1c",c);
}


int clrlnd_i;

void clear_lined()
{
    /*
       initialize linedata: at the beginning of a line
     */

    line_data.wsum = 0;
    line_data.nspaces = 0;
    line_data.nfix = 0;
    line_data.curpos = 0;
    line_data.line_nr = 0;
    line_data.linebuf1[0]='\015';
    line_data.linebuf2[0]='\015';
    line_data.linebuf1[1]='\012';
    line_data.linebuf2[1]='\012';

    for (clrlnd_i=2; clrlnd_i<200; clrlnd_i++) {
       line_data.linebuf1[clrlnd_i]='\0'; line_data.linebuf2[clrlnd_i]='\0';
    }
    ncop  = 0;

}   /* i */


void clear_linedata()
{
    /*
       initialize linedata: before all disecting...
     */

    line_data.kind   = 0;
    line_data.last   = 0.;
    line_data.former = 0.;
    line_data.vs     = 0.;
    central.d_style =  0;  /* dominant style */
    line_data.c_style = 0; /* style */
    /* hier style en dominant stellen */

    clear_lined();
}



