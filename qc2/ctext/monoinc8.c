/* c:\qc2\ctext\monoinc8.c

   void  zenden2( void )
      row_test(cb);
      setrow( e2, line_uitvul[1]-1 );
      showbits(e2);
      NJ_test (cb)
      NK_test (cx)
      GS2_test(cb)
   void  displaym()
      scherm2();
      pri_lig( & mm );
      scherm3();
   void  disp_schuif( )
   void  disp_vsp(char sp)
   int   zoek( char l[], unsigned char s, int max )
   void  dispmat(int max)
   float read_real ( void )
   void  wis(int r, int k, int n)
   int   verdeel ( void )  /*  int  qadd = number of possible 9 spaces
   int   keerom ( void )
   char  afscheid(void)
   void  tzint1()
   void  tzint2( float maxbreedte )
   unsigned char  berek( char cy, unsigned char w )
   void  move( int j , int k )
   unsigned char  alphahex( char dig )
   void  print_c_at( int rij, int kolom, char c)
   void  calc_kg ( int n )
       adjust (int add, float add )
   void  store_kg( void )
   void  ontcijf( void )
   void  clear_lined()
   void  clear_linedata()
   void p_error( char *error )

*/

void p_error( char *error )
{
   print_at(1,1,error);
   while ( ! kbhit () ) ;

   exit(1);
}



/*zenden2*/
/*
    read tempfile ....
    delete redundant code
    add code to correct the places of the wedges

	 row_test(cb);
	 setrow( e2, line_uitvul[1]-1 );
	 showbits(e2);
	 NJ_test (cb)
	 NK_test(cx)
	 GS2_test(cb)

*/

int znd_i,znd_j;

    /* values needed to cast */
unsigned char  znd_cb[5];
unsigned char  znd_cx[5];
unsigned char  znd_e1[5];
unsigned char  znd_e2[5];
unsigned char  znd_p1, znd_p2, znd_p3, znd_p4;
unsigned char  znd_line_uitvul[2];
unsigned char  znd_t_u[2];
unsigned char  znd_char_uitvul[2];
/* unsigned char  znd_unit_add = 0; */

/* char znd_start_regel = 0; */

int znd_lt, znd_ut, znd_tut;
int znd_r0,znd_r1;


void zenden2( void )
{

    znd_char_uitvul[0]=3;
    znd_char_uitvul[1]=8;

    for (znd_i = codetemp; znd_i>=0; znd_i--) {

	/* read two specified records from temp-file */

	recseek = (long) ((znd_i - 1) * recsize);
	fseek( recstream, recseek, SEEK_SET );
	fread( &temprec, recsize, 1, recstream );
	for ( znd_j=0 ; znd_j<5 ; znd_j++)
	   znd_cb[znd_j] = temprec.mcode[znd_j];

	recseek = (long) ((znd_i - 2) * recsize);
	fseek( recstream, recseek, SEEK_SET );
	fread( &temprec, recsize, 1, recstream );
	for (znd_j=0; znd_j<5 ; znd_j++)
	   znd_cx[znd_j] = temprec.mcode[znd_j];

	/* these two records may contain information about the
	   position of the adjustment wedges

	   double justification:
	      NKJ gk u2
	      NJ  g  u1
	      "beginning" of a line
	   single justification:
	      NJ  k  u2
	      NK  g  u1
	      "character or space with S-needle"

	   if the wedges are in the desired place
	   the justifacation-code can be ignored

	   if the wedges are not placed correct, extra code is added

	   */

	   /* for (znd_i=0; buff[znd_i] != -1 ; ) {  */
	   /*
	      for (znd_j=0;znd_j<=3;znd_j++) {
		 znd_cx[znd_j]=buff[znd_i+4];
		 znd_cb[znd_j]=buff[znd_i++];
	      }
	    */
	znd_p1=1; znd_p2=0; znd_p3=0; znd_p4=0;
	znd_r1 = row_test(znd_cb);
	znd_r0 = row_test(znd_cx);
	/* printf("%2d/%2d ",znd_r0,znd_r1);*/

	if ( (NJ_test ( znd_cb) + NK_test(znd_cb)) == 2) {
	   /* printf("Beginning of a line found\n
	      NKJ in the first code ...\n");
	    */
	   znd_line_uitvul[1] = znd_r0;
	   znd_line_uitvul[0] = znd_r1;
	   znd_char_uitvul[0] = znd_line_uitvul[0];
	   znd_char_uitvul[1] = znd_line_uitvul[1];
	   znd_p1=1; znd_p2=1; /* both codes will be needed */
	} else {
	   if ( (NJ_test (znd_cb) + NK_test(znd_cx) ) == 2) {
	       znd_t_u[1] = znd_r0;
	       znd_t_u[0] = znd_r1;
	       znd_tut = znd_r0*15+znd_r1;
	       znd_ut = 15*znd_char_uitvul[1] + znd_char_uitvul[0];
	       if (znd_tut == znd_ut ) {
		   /*  printf("wedges in right position:\n");
		       printf("no adjustment code is sent\n");
		       printf("code is ignored \n");
		       */
		  znd_p1=0; znd_p2=0; znd_i+=4;
	       } else {
		  /*  printf("wedges out of position:\n");
		      printf("adjustment code %2d/%2d must be sent.\n",
			     znd_t_u[1],znd_t_u[0]);
		   */
		  znd_p1=1; znd_p2=1; /* both to caster */
	       }
	       znd_char_uitvul[0] = znd_t_u[0];
	       znd_char_uitvul[1] = znd_t_u[1];
	   } else {
	      if ( GS2_test(znd_cb) == 1) {
		 /*
		    a variable space found
		  */
		 znd_lt = 15*znd_line_uitvul[1] + znd_line_uitvul[0];
		 znd_ut = 15*znd_char_uitvul[1] + znd_char_uitvul[0];
		 if ( znd_ut != znd_lt ) {
		    /*
		       make extra code to adjust the wedges to the
		       right position to cast variable spaces

		       no difference between the "old" systems and unit-adding

		       NJ   u2 k    NJ   u2 k
		       NK g u1      NK g u1

		       though the function of the code is different

		       */
		    /* printf("gs2 = variable space: wedges in wrong position\n");
		       printf("      extra code is generated during casting");get_line(); */

		    znd_e2[0]= 0x44; /* NJ; */
		    znd_e2[1]= 0; znd_e2[2]= 0;
		    znd_e2[3]= 0x01; /* k */
		    znd_e1[0]= 0x48; /* NK; */
		    znd_e1[1]= 0x04; /* W0075 */
		    znd_e1[2]= 0; znd_e1[3]= 0x0;

		    setrow( znd_e2, znd_line_uitvul[1]-1 );
		    znd_p3 =1;
		    showbits(znd_e2);
		    setrow( znd_e1, znd_line_uitvul[0]-1);
		    showbits(znd_e1);
		    znd_p4 = 1;
		    znd_char_uitvul[0] = znd_line_uitvul[0];
		    znd_char_uitvul[1] = znd_line_uitvul[1];
		 } else {
		    znd_p1=1; znd_p2=0;

		    /*    printf("gs2 = variable space:\n");
			  printf("wedges in right position");
			  get_line();    */
		 }
	      }
	   }
	}
	if (znd_p3==1) {  /* NJ k u2 extra justification code */
	    showbits(znd_e2);
	       /* to -> codefile */
	    for (znd_j=0;znd_j<5;znd_j++)
	       coderec.mcode[znd_j]=znd_e2[znd_j];
	    fwrite( &coderec,
		     recsize, 1,
		     foutcode  );
	}
	if (znd_p4==1) {  /* NK g u1 extra justification code */
	    showbits(znd_e1);
		 /* to -> codefile */
	    for (znd_j=0;znd_j<5;znd_j++)
		 coderec.mcode[znd_j]=znd_e1[znd_j];
	    fwrite( &coderec, recsize, 1, foutcode  );
	}
	if (znd_p1==1) {  /* code from temp-file */
	    showbits(znd_cb);
		 /* to -> codefile */
	    for (znd_j=0;znd_j<5;znd_j++)
		 coderec.mcode[znd_j]=znd_cb[znd_j];
	    fwrite( &coderec, recsize, 1, foutcode  );
	}
	if (znd_p2==1) {
	    showbits(znd_cx);  /* code from temp-file */
		 /* to -> codefile */
	    for (znd_j=0;znd_j<5;znd_j++)
		 coderec.mcode[znd_j]=znd_cx[znd_j];
	    fwrite( &coderec, recsize, 1, foutcode  );

	    znd_i --; /* this time two records are written */
	}

	/*
	  printf("lu %2d/%2d cu %2d/%2d \n",znd_line_uitvul[0],znd_line_uitvul[1],
		   znd_char_uitvul[1],znd_char_uitvul[0]);
	  if ('#'==getchar() ) exit(1);
	*/
    }
} /* end zenden2 */


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

int ds_i;

void disp_schuif( )
{

   print_at(22,1,"plaats  = ");
   print_at(16,1,"nschuif = ");
   for (ds_i=0;ds_i<nschuif;ds_i++) printf("     %1d ",ds_i );
   print_at(17,1,"ligl[ns-1]");
   for (ds_i=0;ds_i<nschuif;ds_i++) printf("     %1d ",ligl[ds_i] );
   print_at(18,1,"rb[plrb[i]");
   for (ds_i=0;ds_i<nschuif;ds_i++) printf("     %1c ",readbuffer[ plrb[ds_i] ]);
   print_at(19,1,"plrb[ns-1]");
   for (ds_i=0;ds_i<nschuif;ds_i++) printf("   %3d ",plrb[ds_i] );
   print_at(20,1,"schuif[  ]");
   for (ds_i=0;ds_i<nschuif;ds_i++) printf("%6.4f ",schuif[ds_i]);
   print_at(21,1,"pcop[]    ");
   for (ds_i=0;ds_i<nschuif;ds_i++) printf("  %4d ",  pcop[ds_i]);
   print_at(22,1,"ligk[]    ");
   for (ds_i=0;ds_i<nschuif;ds_i++) printf("     %1d ",ligk[ds_i] );
}  /* i */



void disp_vsp(char sp)
{
   print_at(12,1,"                                           ");
   print_at(12,1,sp == ' ' ? "VARSP " : "FIXED ");
   printf("nsch-1 %2d ",nschuif-1);
   printf("wsum %8.5f letters %3d ncop %4d ",
		     line_data.wsum, line_data.line_nr, ncop);
   if ( '#'==getchar() ) exit(1);
}





/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *                                                                       *
 *     float adjust   (  width[row], float add )  27 feb 2004                  *
 *                                                                       *
 *       limits to the adjusment of character:                           *
 *                                                                       *
 *      largest reduction : 1/1  2/7 = 35 * .0005" = .0185"              *
 *      neutral           : 3/8      = 0.000"                                *
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


int zoek( char l[], unsigned char s, int max )
{

   zoek_rcgevonden = FALSE;
   zoek_rcnr=-1;
   zoek_rcsum = 0;
   zoek_rcst = s;

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
	   zoek_rcsum += abs( l[zoek_rci]
			     - matrix[zoek_rcnr].lig[zoek_rci] );
      }

	/*
	   if (zoek_rcsum < 2 ) {
	      printf("Sum = %6d nr = %4d ",zoek_rcsum,zoek_rcnr);
	      ce();
	   }
	 */

      zoek_rcgevonden = ( (zoek_rcsum == 0 ) &&
		  (matrix[zoek_rcnr].srt == zoek_rcst )) ;

      if (zoek_rcnr > 450) exit(1);
   }
      while ( (zoek_rcgevonden == FALSE) && ( zoek_rcnr < max - 1 ) );

   if (zoek_rcgevonden == TRUE){
      return ( zoek_rcnr );
   } else
      return ( -1 );
}   /* zoek */

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
    return (atof(readbuffer));
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




/*
    verdeel (divide)

    divides the room left at the end of a line

    output in verdeelstring[]

    alternating squares with 9 spaces, as much as possible

 */

unsigned int vrds1, vrds2, vrds3, vrdi, vrdn;


int  verdeel ( void )  /*  int  qadd = number of possible 9 spaces
			   unsigned char var = number variable spaces
		   */
{

    vrdn=2;

    for ( vrdi = vrdn ; vrdi<100 ;vrdi++ ) verdeelstring[vrdi]=0;

    left = ( qadd > var ) ? ( qadd - var ) : 0 ;

    vrds1=0;  vrds2=0; vrds3=0;

    while ((left > 0 ) || (var > 0 ) ) {
	if (left >= 2 ) {  /* a square */
	   vrds1++;
	   left -=2;  /* 18 = 2 * 9 */
	   verdeelstring[vrdn++]='#';
	}
	if (var > 0) { /* a variable space */
	     vrds2++;   var --;
	     verdeelstring[vrdn++]='V';
	} else {
	    if (left > 0 ) { /*  fixed space */
		vrds3++;  left --;
		verdeelstring[vrdn++]='F';
	    }
	}
    }
    return ( vrdn );
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

char afsch_c;

char afscheid(void)
{

   do {
      printf("\n\n\n\n        another text < y/n > ? ");
      afsch_c = getchar();
   }
     while ( afsch_c != 'n' && afsch_c != 'y' && afsch_c != 'j');
   return ( afsch_c );
}



void tzint1()
{
    cls();
    printf(" tzint1 : gegevens ");
    printf(" set         %4d \n",  central.set);
    printf(" matrijzen   %4d \n",  central.matrices);
    printf(" syst        %4d \n",  central.syst);
    printf(" adding      %4d \n",  central.adding);
    printf(" pica_cic       %1c\n",central.pica_cicero);
    printf(" line width  %4d \n",  central.lwidth);
    ce();
}


void tzint2( float maxbreedte )
{


   print_at(23,1,"tzint2: marge: ");
   printf("%7.5f ncop %3d ", line_data.wsum, ncop );
   printf("maxbreedte = %7.5f line = %7.5f c = %1c ",
	  maxbreedte, central.inchwidth, readbuffer[0] );

   print_at(24,1,"");
   printf( line_data.wsum < maxbreedte ? "kleiner" : "groter");
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

int mv_i;

void move( int j , int k )
{

   if ( nschuif < 10 ) {           /* store */
       ligl  [ nschuif  ] = k;
       pcop  [ nschuif  ] = ncop;
       plrb  [ nschuif  ] = j;
       schuif[ nschuif++] = line_data.wsum;
   }
   else {
       for (mv_i=0; mv_i<9 ; mv_i++) {      /* only last 10... move */
	  ligl  [mv_i] = ligl  [mv_i+1] ;
	  pcop  [mv_i] = pcop  [mv_i+1] ;
	  plrb  [mv_i] = plrb  [mv_i+1] ;
	  schuif[mv_i] = schuif[mv_i+1] ;
       }
       ligl  [ nschuif -1 ] = k;
       pcop  [ nschuif -1 ] = ncop;
       plrb  [ nschuif -1 ] = j;
       schuif[ nschuif -1 ] = line_data.wsum;
   }
}  /* i ft */

unsigned char alpha_add;

unsigned char  alphahex( char dig )
{
   alpha_add = 0;

   if ( dig >= 'A' && dig <='F' )
	dig +=  ('a'-'A');
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

void calc_kg ( int n )
{
   adjust ( central.set < 48 ? wig[1] : wig[0] ,
	    ((float) idelta) /((float) n)
	   );
}

void store_kg( void )
{
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
    for (clrlnd_i=0; clrlnd_i< 15; clrlnd_i++) {
       ligl[clrlnd_i] = 0;
       pcop[clrlnd_i] = 0; /* pointers naar cop */
       plrb[clrlnd_i] = 0;
       ligl[clrlnd_i] = 0;
    }
    npcop = 0;
    nplrb = 0;
    ncop  = 0;

    /* schuif reinigen */
    for (clrlnd_i=0;clrlnd_i<10;clrlnd_i++) schuif[clrlnd_i]=0;
    nschuif = 0;
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

    clear_lined();
}



