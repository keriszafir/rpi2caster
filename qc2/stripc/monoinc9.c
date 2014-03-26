/* monoinc9

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


   int lus ()
      alphahex( char )
      berek( )
      move(   , 1)
      line_data.wsum += gen_system ( lus_du,    / * column * /
					lus_cu, / * row  * /
					lus_bu  / * width char * /
				       );
      dispcode( letter );
      ce();
      disp_schuif(  );
      calc_maxbreedte ( );
      fixed_space();

      commands in the input text-files:

      ^01 = roman, ^01 = italic ^02 = small caps ^03 = bold
      ^ln = length ligatures line_data.nlig n = 1, 2, 3
      ^mx = next n lines start at lenght of this line
		    line_data.vs
      ^pS = start paragraph
      ^pE = End Paragraph

      kerning:

      ^+n = add next char 1-9 units
      ^-n = substract next char(s) 1/4 - 8/4 units
      ^#x = add x * 18 units, if possible
      ^=x = add x * 9 units, if possible

      ^rx = repeat signal for kerning (x=alphahex) after: ^+x && ^-x


      ^CR = Carriage Return: end line here
      ^CC = place text in Center Line
      ^CL = left filled line



      ^EF = end of file

      ^Fx = '_' fixed spaces = 3 + x * .25  points
			      x = alpha-hexadicimaal  0123456789abcdef

      ^vx = '_' fixed spaces set < 10



      ^Lx = x empty lines  x = decimaal

      ^Rx = repeat signal right margin
	       x = alphahex( )
      ^Wx = width right margin
	    x = number of pica's/cicero's/fournier's (x=alphahex)


      ^8x   insert ascII-code on its place
      ^9x ^ax ^bx ^cx ^dx ^ex ^fx

      soep
      stoep
      koek
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


void  dump_cop()
{
;
}

int marge_i, marspc, mr_18, mr_s , m_i, m_rest ;
int mu1, mu2;
unsigned char u_1[4], u_2[4], mgs[4] ;



void  marge ( float length, unsigned char strt )
{

    mar_units   = (int) (.5 + ( length * 5184. / (float) central.set ) );

    mar_totunit += (int)
	( .5 + ( line_data.wsum * 5184. / (float) central.set ) );


    mr_18=0;
    mr_s =0;


    for (m_i=0; m_i<4; m_i++) {
	mgs[m_i] = 0;
	u_1[m_i] = 0;
	u_2[m_i] = 0;
    }
    mgs[1] = 0xa0; /* GS  */
    mgs[2] = 0x20; /*   2 */
    u_1[0] = 0x48; /* NK  */
    u_1[1] = 0x04; /* 0075 */

    u_2[0] = 0x4a; /* NKJ */
    u_2[3] = 0x01; /* 0005 */

    switch ( strt ) {
       case 0 : /* line left alined
		   begin regel variabele spaties */

	  mr_s = mar_units / 6 ;
	  m_rest = mar_units % 6;
	  if ( mr_s > 5 ) {
	     mr_18 = 1;
	     mr_s  -= 3;
	  }

	  line_data.nspaces += mr_s;
	  if ( line_data.nspaces > 0 ) {
	     mu1 = 0;           /* 2000/5184 */
	     mu2 = 53 + (int) (.5 +
		.385802469 * m_rest * central.set /
			 (float) line_data.nspaces  ) ;
	     while ( mu2  > 15 ){
		mu2 -= 15;
		mu1 ++;
	     }
	  } else {
	     mu1 = 3;
	     mu2 = 8;
	  }
	  setrow( u_1, mu1 );
	  setrow( u_2, mu2 );

	  if (mr_18 == 1) {
		for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i] = 0;
		store_code(); /* opslaan O-15 */
	  }

	  for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i]= mgs[m_i];
	  for ( marge_i =0; marge_i < mr_s; marge_i++) {
	     /* opslaan spaties */
	     store_code();
	  }

	  /* uitvulling uitrekenen
	       verdelen over:
	       mr_s + varspaties regel
	       en achter cop plaatsen
	       line_data.nspaces ?
	   */

	  for ( marge_i =0; marge_i < 3; marge_i++) {
	     cop[ncop++] = u_1[marge_i]; /* opslaan */
	  } /* NK 0075 u_1 */
	  for ( marge_i =0; marge_i < 3; marge_i++) {
	     cop[ncop++] = u_2[marge_i]; /* opslaan */
	  } /* NKJ 0075 u_2 0005 => end line */

	  line_data.wsum = central.inchwidth;

	  break;
       case 1 : /* line right alined
		   eind regel variable spaties */


	  mr_s = mar_units / 6 ;
	  m_rest = mar_units % 6;
	  if ( mr_s > 5 ) {
	     mr_18 = 1;
	     mr_s  -= 3;
	  }
	  line_data.nspaces += mr_s;
	  if (line_data.nspaces > 0 ) {
	     mu1 = 0;           /* 2000/5184 */
	     mu2 = 53 + (int) (.5 +
		.385802469 * m_rest * central.set/ (float) line_data.nspaces  ) ;
	     while ( mu2  > 15 ){
		mu2 -= 15;
		mu1 ++;
	     }
	  }
	  else {
	     mu1 = 3;
	     mu2 = 8;
	     printf("nspaces = 0 ");
	     if (getchar()=='#') exit(1);
	  }
	  setrow( u_1, mu1 );
	  setrow( u_2, mu2 );

	  for ( marge_i =0; marge_i < mr_s; marge_i++) {
	     cop[ncop++] = mgs[marge_i]; /* opslaan */
	  }
	  if (mr_18 == 1) {
	     cop[ncop++] = 0; /* opslaan O-15 */
	  }

	  for ( marge_i =0; marge_i < 3; marge_i++) {
	     cop[ncop++] = u_1[marge_i]; /* NK 0075 u1 */
	  }
	  for ( marge_i =0; marge_i < 3; marge_i++) {
	     cop[ncop++] = u_2[marge_i]; /* NKJ 0075 u2 0005 */
	  }

	  line_data.wsum = central.inchwidth;
	  break;
       case 2 : /* centreren */
	  mr_s = mar_units / 6 ;
	  m_rest = mar_units % 6;

	  if (mr_s % 2 == 1 ) {
	      mr_s --;
	      m_rest += 6;
	  }

	  if ( mr_s > 10 ) {
	     mr_18  = 1;
	     mr_s  -= 6;
	  }
	  mr_s  /= 2;


	  line_data.nspaces += 2*mr_s;
	  if (line_data.nspaces > 0 ) {
	     mu1 = 0;           /* 2000/5184 */
	     mu2 = 53 + (int) (.5 +
		.385802469 * m_rest * central.set/ (float) line_data.nspaces  ) ;
	     while ( mu2  > 15 ){
		mu2 -= 15;
		mu1 ++;
	     }
	  }
	  else {
	     mu1 = 3;
	     mu2 = 8;
	     printf("nspaces = 0 ");
	     if (getchar()=='#') exit(1);

	  }
	  setrow( u_1, mu1 );
	  setrow( u_2, mu2 );

	  if (mr_18 == 1) {
	     for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i]= 0;
	     store_code(); /* opslaan O-15 */
	  }

	  for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i]= mgs[m_i];
	  for ( marge_i = 0; marge_i < mr_s; marge_i++) {
	     /* opslaan var spaties */
	     store_code();
	  }

	  /* nu achter cop plaatsen */

	  for ( marge_i =0; marge_i < mr_s; marge_i++) {
	     cop[ncop++] = mcx[marge_i]; /* opslaan GS2 */
	  }
	  if (mr_18 == 1) {
	     cop[ncop++] = 0; /* opslaan O-15 */
	  }

	  for ( marge_i =0; marge_i < 3; marge_i++) {
	     cop[ncop++] = u_1[marge_i]; /* NK 0075 u1 */
	  }
	  for ( marge_i =0; marge_i < 3; marge_i++) {
	     cop[ncop++] = u_2[marge_i]; /* NKJ 0075 u2 0005 */
	  }

	  line_data.wsum = central.inchwidth;
	  break;
       case 3 : /* marge begin regel gedefineerde afstand */
	  /* kan naar cop hoeft echter niet
	       uitvulling berekenen naar mr_s
	       uitvulling telkens na de code tussenvoegen
	       ncop zal nog 0 zyn...

	       */

	  mr_s   = mar_units / 6 ;
	  m_rest = mar_units % 6;
	  if ( mr_s > 5 ) {
	     mr_18 = 1;
	     mr_s  -= 3;
	  }
	  if (mr_s > 0 ) {
	     mu1 = 0;           /* 2000/5184 */
	     mu2 = 53 + (int)
		(.5 + .385802469 * m_rest * central.set / (float) mr_s ) ;
	     while ( mu2  > 15 ){
	       mu2 -= 15;
	       mu1 ++;
	     }
	  }
	  else {
	     mu1=3;
	     mu2=8;
	     printf("nspaces = 0 ");
	     if (getchar()=='#') exit(1);

	  }
	  setrow( u_1, mu1 );
	  setrow( u_2, mu2 );

	  if (mr_18 == 1) {
	     for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i]= 0;
	     store_code(); /* opslaan O-15 */
	  }

	  /* single justification for the var spaces */
	  u_2[0] = 0x44;
	  u_2[0] = 0x00;


	  for ( marge_i =0; marge_i < mr_s; marge_i++) {
	     for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i]= mgs[m_i];
	     store_code();
	     for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i]= u_1[marge_i];
	     store_code();
	     for ( m_i = 0 ; m_i < 4; m_i++) mcx[m_i]= u_2[marge_i];
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

     /*
	      mcx[0] = cop[tst_i ++];
	      mcx[1] = cop[tst_i ++];
	      mcx[2] = cop[tst_i ++];
	      mcx[3] = cop[tst_i ++];
	      mcx[4] = 0x0f;
	      store_code();
      */
}

void  einde_line()
{
;
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





int  lus( char ctest )
{

   lus_geb = t3j;

   switch ( ctest )
   {
      case '\00' :  /* ignore all control characters */
      case '\01' :
      case '\02' :
      case '\03' :
      case '\04' :
      case '\05' :
      case '\06' :
      case '\07' :
      case '\010':
      case '\011':
      case '\012':  /* linefeed = ignored */
      case '\013':
      case '\014':
      case '\016':
      case '\017':
      case '\020':
      case '\021':
      case '\022':
      case '\023':
      case '\024':
      case '\025':
      case '\026':
      case '\027':
      case '\030':
      case '\032':
      case '\033':
      case '\034':
      case '\035':
      case '\036':
      case '\037':
	 t3j ++;
	 break;
      case '\015':  /* carriage return */
	 if (line_data.para == 0) {
	    /* */
	    /* margin (central.inchwidth - line_data.wsum, 1 ); */
	    t3j++;
	 } else {   /* flat text : ignore */
	    readbuffer[t3j]=' ';
	    t3j--;
	 }
	 break;
		    /* \015 = 13 decimal = CR */

      case  '@' :  /* all commands  */
	 luscy = readbuffer[t3j+1];
	 luscx = readbuffer[t3j+2];

	 /*
	 print_at(12,1,"ctest =^ ");
	 printf(" t3j = %3d luscy = %1c luscx = %1c ",t3j,luscy,luscx);
	 if ('#'==getchar()) exit(1);
	  */

	 switch ( luscy )   /* readbuffer[t3j+1] */
	 {
	    case 'p' :  /* paragraph */
	       switch (luscx) {
		  case 'S' :   /* on */
		    line_data.para = 1;
		    break;
		  case 'E' :   /* off */
		    line_data.para = 0;
		    /* end of the paragraph: fill the line
		       dump_cop ();
		       lusl = central.inchwidth - line_data.wsum;
		       marge (lusl, 1);
		       einde_line ();


		    */
		    margin ( (central.inchwidth - line_data.wsum) , 1 );
		    break;
	       }
	       break;
	    case '0' :  /*  ^00 = roman
			    ^01 = italic
			    ^02 = lower case to small caps
			    ^03 -> bold
			    @04 -> superior chars
			 */
	       lusikind = luscx - '0';
	       if (lusikind > 3 ) lusikind = 0;
	       if (lusikind < 0 ) lusikind = 0;
	       line_data.kind = (unsigned char) lusikind;
	       break;
	    case 'L' :
	       if (luscx >='0' && luscx<='9') {
		   line_data.vs   = luscx - '0';
		   line_data.last = central.inchwidth;
	       }
	       break;
	    case 'R' : /* repeat-signal right margin */
	       lus_lw = alphahex( luscx );
	       if (lus_lw >= 0 ) {
		   line_data.rs   += lus_lw ;
	       }
	       break;
	    case 'W' : /* calculate width right margin
			     in inches
			  luscx = 0-15 pica/cicero
			  */

	       lus_rlw = (float) ( alphahex( luscx ) );
	       switch (central.pica_cicero ) {
		  case 'p' : lus_rlw *= .1776;  /* .0148 */
		    break;
		  case 'd' : lus_rlw *= .16284; /* .01357 */
		    break;
		  case 'f' : lus_rlw *= .16668; /* .01389 */
		    break;
	       }
	       line_data.right = lus_rlw ;
	       break;
	    case 'm' :  /* @mn -> next n lines start at lenght
				     this line
			      unsigned char vs;
			      0: no white
			     >0: add last white beginning line
			    */
	       lus_lw = alphahex( luscx );
	       if (lus_lw > 0) {
		  line_data.last = line_data.wsum ;
		  line_data.vs   = lus_lw;
	       }
	       break;
	    case '+' :  /* ^+1 -> add next char 1-9 units
			    */
	       lusaddw = 0.;
	       if (luscx > '0' && luscx <= '9') {
		   lusaddw =  (float) (luscx - '0');
		   line_data.letteradd += lusaddw;
		   if (central.set > 48 ) {
		      while (line_data.letteradd < -1. )
			 line_data.letteradd += .25;
		   } else {
		      while (line_data.letteradd < -2. )
			 line_data.letteradd += .25;
		   }
		   line_data.add = 1;
	       }
	       break;
	    case '-' :  /* ^-1 -> subtract 1-8 1/4 units
			    */
	       lusaddw = 0.;
	       if ( luscx >'0' && luscx <'9') {
		   lusaddw =  (float) (luscx - '0');
		   line_data.letteradd -= lusaddw * .25;
		   line_data.add = 1;
	       }
	       lusaddw *= - .25;
	       break;
	    case 'r' : /* repeat signal for "kerning" */
	       if (fabsoluut(lusaddw) > .1) {
		   line_data.add = alphahex( luscx );
	       }
	       break;
	    case '#' :  /* @#n add n times 18 units squares alpha-hex .... */

	       if ( ( line_data.wsum +
		    ( (float) (alphahex(luscx) * 18 * central.set) ) / 5184.)
		      > central.inchwidth ) {

		  margin(central.inchwidth - line_data.wsum, 1 );
		  /* line_data.wsum = central.inchwidth; */
	       } else {

		  lusaddsqrs = berek( luscx, 18 );
		  if (lusaddsqrs != 0 ) {
		     move( t3j,0 );
		     for ( lus_i = 0; lus_i < lusaddsqrs
			/*
			   function berek controls overflow
			   en de maxbreedte mag niet overschreden
			   worden...
			   !!!!!!!!!!!!!

			*/
			   ; lus_i++ ){

			cop[ncop++] = 0;  /* O15 */
			cop[ncop++] = 0;
			cop[ncop++] = 0;
			cop[ncop++] = 0;
			line_data.linebuf1[lnum]   = '#';
			line_data.linebuf2[lnum++] = ' ';
			line_data.line_nr ++;
			line_data.wsum +=
			    ( (float) (18 * central.set) )/5184.;
		     }
		  }
	       }
	       /* O-15 = default 18 unit space */
		  /* printf("lusaddsqrs = %2d width = %8.2f",lusaddsqrs,
			       line_data.wsum );
		       ce();
		      */
	       break;
	    case '=' :  /* ^=n -> add n half squares alphahex... */

	       if ( ( line_data.wsum +
		      ((float) ( alphahex(luscx) * 9 * central.set ) ) / 5184.)
		      > central.inchwidth ) {

		  margin(central.inchwidth - line_data.wsum, 1 );

		  /* line_data.wsum = central.inchwidth; */
	       } else {

		  lusaddsqrs = berek( luscx, 9 );
		  if (lusaddsqrs != 0 ){
		     move(t3j,0);
		     for ( lus_i = 0; lus_i < lusaddsqrs
			/* and maxbreedte niet overschreden
			   !!!!!!!!!!!!!
			 */
			; lus_i++ ) {
			cop[ncop++] = 0;
			cop[ncop++] = 0x80; /* G */
			cop[ncop++] = 0x04; /* 5 */
			cop[ncop++] = 0;
			line_data.linebuf1[lnum   ] = '=';
			line_data.linebuf2[lnum++ ] = ' ';
			line_data.line_nr++ ;
			line_data.wsum +=
			   ((float) ( 9 * central.set) ) / 5184.;
		     }
		  }
	       }
	       break;
	    case 'C' :  /* end line here */
	       /* ^CR  =  end line here  */
	       switch ( luscx ) {
		  case 'R' :
		     /*
		     dump_cop();
		     marge ( central.inchwidth - line_data.wsum, 1 );
		     einde_line();
		     */
		     margin (central.inchwidth - line_data.wsum, 1 );


		     break;
		  case 'C' :
		     /*
		     lusl = (central.inchwidth - line_data.wsum)*.5;
		     marge ( lusl, 0 );
		     dump_cop();
		     marge ( lusl, 1 );
		     einde_line();
		      */
		     margin ((central.inchwidth - line_data.wsum)*.5 , 0 );
		     margin ((central.inchwidth - line_data.wsum)*.5 , 1 );

		     break;
		  case 'L' :
		     /*
		     lusl = central.inchwidth - line_data.wsum ;
		     marge ( 0 );
		     dump_cop();
		     einde_line();
		     */
		     /* dump cop */
		     /* end line */
		     margin ((central.inchwidth - line_data.wsum)*.5 , 0 );

		     break;
	       }

	       /* ^CL  = place text in center line
		  -> central placement of the text in the line
		*/
		  break;
	    case 'E' :  /* EOF reached */
	       printf("End wsum = %10.4f ",line_data.wsum);
	       /*
	       lusl = central.inchwidth - line_data.wsum;
	       marge ( lusl, 1 );

		*/
	       margin (central.inchwidth - line_data.wsum, 1 );

	       t3j++; /* een verder zetten */
		 /* input file sluiten
		  rest wegschrijven naar output file
		  vlag zetten, zodat het programma stopt

		  */


	       break;

	    case 'F' : /* ^Fn -> '_' =>
			   fixed spaces = 3 + n * .25  points
			      n = alpha-hexadicimaal  0123456789abcdef
			   */
	       datafix.wsp = 3 + alphahex( luscx ) * .25 ;
	       central.fixed = 'y';
	       fixed_space();
	       break;
	    case 'l' :  /* ^ln -> length ligatures his line
			      line_data.nlig
			      1, 2, 3
			    */
	       line_data.nlig = ( luscx > '0' && luscx < '4' ) ?
				  luscx - '0' :  3;
	       break;
	    case '8' :  /* insert ascII-code on its place  */
	    case '9' :
	    case 'a' :
	    case 'b' :
	    case 'c' :
	    case 'd' :
	    case 'e' :
	    case 'f' :
	       /* the two next chars will not be evaluated a second time */

	       readbuffer[t3j  ] = '\00' ;
	       readbuffer[t3j+1] = '\00' ;
	       readbuffer[t3j+2] = 16*alphahex( luscy ) + alphahex( luscx );
	       t3j --;
	       break;

	 }  /* switch ( readbuffer[t3j+1] ) = luscy */

	 t3j += 3;
	 break;
      case ' ' :              /* variable space set <= 12: GS2, */
	 move(t3j,1);    /* store results */

	 if (central.set <= 48 ) {
	    line_data.wsum +=
		      ( (float) (wig[1] * central.set) ) / 5184. ;

	    cop[ncop++] = 0;
	    cop[ncop++] = 0xa0; /* GS */
	    cop[ncop++] = 0x20; /* 02 van 02 -> 20 6 aug 2004  */
	    cop[ncop++] = 0;
	 } else {             /* set > 12: GS1  */
	    line_data.wsum +=
		      ( (float) ( wig[0] * central.set) ) / 5184. ;
	    cop[ncop++] = 0;
	    cop[ncop++] = 0xa0; /* GS */
	    cop[ncop++] = 0x40; /*  1 */
	    cop[ncop++] = 0;
	 }
	 plaats[lnum] = t3j;
	 plkind[lnum] = kind;
	 line_data.nspaces ++;
	 line_data.curpos ++;
	 line_data.linebuf1[lnum  ] = ' ';
	 line_data.linebuf2[lnum++] = ' ';
	 line_data.line_nr ++;
	 t3j++;
	 break;
      case '_' : /* add code for fixed spaces */
	 move(t3j,1);
	 plaats[lnum] = t3j;
	 plkind[lnum] = kind;
	 if (line_data.para == 0) {
	    for ( lus_k=0; lus_k<12; lus_k++ )
	       cop[ncop++] = datafix.code[lus_k];
	    line_data.wsum +=
		  (datafix.wunits * (float) central.set ) / 5184.;
	    line_data.nfix ++;

	    line_data.linebuf1[lnum  ] = '_';
	    line_data.linebuf2[lnum++] = ' ';
	    line_data.line_nr ++;
	 } else { /* line_data.para == 1 */
	    if (central.set <= 48 ) {
	       line_data.wsum +=
		      ( (float) (wig[1] * central.set) ) / 5184. ;
	       cop[ncop++] = 0;
	       cop[ncop++] = 0xa0; /* GS */
	       cop[ncop++] = 0x20; /* 2  van 02 -> 20 6 aug 2004 */
	       cop[ncop++] = 0;
	    } else {             /* set > 12: GS1  */
	       line_data.wsum +=
		      ( (float) ( wig[0] * central.set) ) / 5184. ;
	       cop[ncop++] = 0;
	       cop[ncop++] = 0xa0; /* GS */
	       cop[ncop++] = 0x40; /*  1 */
	       cop[ncop++] = 0;
	    }
	    plaats[lnum] = t3j;
	    plkind[lnum] = kind;
	    line_data.nspaces ++;
	    line_data.linebuf1[lnum  ] = ' ';
	    line_data.linebuf2[lnum++] = ' ';
	    line_data.line_nr ++;
	 }
	 line_data.curpos ++;
	 t3j++;
	 break;
      default :
	 lus_k = line_data.nlig + 1;
	 do {    /* seek all ligatures */
	    lus_k--;
	    for ( lus_i=0; lus_i< 4; lus_i++ ) lus_ll[lus_i] = '\0';
	    for ( lus_i=0; lus_i< lus_k; lus_i++ ) {
	       lus_ll[lus_i] = readbuffer[t3j+lus_i];
	    }
	    uitkomst = zoek( lus_ll, line_data.kind, matmax);
	 }
	    while ( (uitkomst == -1) && (lus_k > 1) ) ;

	 if ( uitkomst == -1 ) {  /* no char found */
	    lus_k = 1;
	    uitkomst = 76; /* g5 is cast */
	    lus_ll[0]=' ';
	 }

	 move(t3j,lus_k);

	 for (lus_i=0;lus_i<lus_k;lus_i++) {  /* store ligature in linebuffer */
	    plaats[lnum] = t3j;
	    plkind[lnum] = kind;
	    line_data.linebuf1[lnum   ] =  lus_ll[lus_i];
	    switch (kind) {
	       case 0 : line_data.linebuf2[lnum ] = ' ' ;
		  break;
	       case 1 : line_data.linebuf2[lnum ] = '/' ;
		  break;
	       case 2 : line_data.linebuf2[lnum ] = '.' ;
		  break;
	       case 3 : line_data.linebuf2[lnum ] = ':' ;
		  break;
	    }
	    lnum++;
	    line_data.line_nr++;
	    t3j++;
	 }

	 lus_bu = (float) matrix[ uitkomst ].w;
	 lus_cu = matrix[uitkomst].mrij;
	 lus_du = matrix[uitkomst].mkolom;

	 if ( line_data.add  > 0 ) {
	    lus_bu += line_data.letteradd;
	    if ( line_data.add == 1 ) {
		 lusaddw = 0.;
		 line_data.letteradd = 0;
	    }
	    line_data.add --;
	 }

	 line_data.wsum += gen_system ( lus_du, /* column */
					lus_cu, /* row  */
					lus_bu  /* width char */
				       );

	 lus_i=0;      /* store generated code */
	 do {
	    cop[ ncop++ ] = cbuff[lus_i++];
	 }
	    while  (cbuff[lus_i] < 0xff);
      break; /* default */


   } /* end switch ctest */


      /*
      lus_k = 0;
      for (lus_i=0; lus_i< ncop ; ) {
	 letter[0] = cop[lus_i++]; letter[1] = cop[lus_i++]; letter[2] = cop[lus_i++];
	 letter[3] = cop[lus_i++]; lus_k ++;
	 print_at(20,1,"");     printf("code %3d ",lus_k);
	 dispcode( letter );
	 ce();
      }
      */

   disp_schuif(  );

   if (lnum>=10) {
	 print_at(22,1,"plt plknd ");
	 for (lus_i = lnum-10; lus_i<lnum; lus_i++)
	    printf(" %4d %1d", plaats[lus_i],plkind[lus_i]);
	 print_at(23,1,"lnum    = ");
	 for (lus_i = lnum-10; lus_i<lnum; lus_i++)
	    printf("  %4d ", lus_i);
	 print_at(24,1,"rb[pl[lus_i]] ");
	 for (lus_i= lnum-10; lus_i<lnum; lus_i++)
	    printf("     %1c ",readbuffer[plaats[lus_i]]);
   }

   calc_maxbreedte ( );

	 /* inwin ruimte spaties - mogelijkheid afbreekteken */
	 /*
	 print_at(22,1,"nspaces ");
	 printf("%2d ",line_data.nspaces);
	 print_at(23,1,"wsum: "); printf("%10.5f maxbreedte = %10.5f line = %10.5f ",
	    line_data.wsum,  maxbreedte, central.inchwidth );
	 */

   return ( t3j - lus_geb) ;
}

/* lus readbuffer2  wsum */


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

    mar_units   = (int) (.5 + ( length * 5184. / (float) central.set ) );
    mar_totunit = (int) (.5 + ( line_data.wsum * 5184. / (float) central.set ) );


    if (central.set < 49 ) {
       mar_maxsub = (float) (line_data.nspaces * 2 * central.set);
    }  else {
       mar_maxsub = (float) (line_data.nspaces * central.set);
    }

    mar_maxsub /= 5184.;
    mar_subu = (int) (.5 + ( mar_maxsub * 5184. / (float) central.set ) );

    if ( line_data.wsum - mar_maxsub > central.inchwidth ) {
       p_error("line too large in margin ");
    }

    fill_line ( mar_units );

    mar_nr = keerom();

    /*
    print_at(11,30,"mar_nr =");
    printf(" %3d units ",mar_nr,mar_units);
    if (getchar()=='#') exit(1);

     */


    for (mar_j=0; mar_j< mar_nr; mar_j++)
    {
       mar_com = '0';
       switch (strt)
       {
	  case 0 : /* strt == 0 */
	     if ( ( reverse[mar_j] >  '0' && reverse[mar_j] <= '9') ||
	       ( reverse[mar_j] >= 'a' && reverse[mar_j] <= 'f') )
	     {
		if ( ( mar_nr - mar_j ) <= 2 )
		{
		   mar_com = (mar_j == ( mar_nr-1 ) )  ? '2' : '1';
		} else
		{
		   mar_com = (mar_j == 0 ) ? '1': '2';
		}
	     }
	     break;
	  case 1 :
	      /* strt == 1 */
	     if ( ( reverse[mar_j] >  '0' && reverse[mar_j] <= '9') ||
	       ( reverse[mar_j] >= 'a' && reverse[mar_j] <= 'f') )
	     {
		if ( ( mar_nr - mar_j ) <= 2 )
		{
		   mar_com = ( mar_j == ( mar_nr-1 ) )  ? 'b' : 'a';
		} else
		{
		   mar_com = ( mar_j == 0 ) ? 'a': 'b';
		}
	     }
	     break;
	  case 2 :
	     break;
       }

       translate( reverse[mar_j] , mar_com );

       switch ( reverse[mar_j] ) {
	    case '#' :
	      line_data.linebuf1[lnum   ] = '#' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
	    case 'F' :
	      line_data.linebuf1[lnum   ] = ' ' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
	    case 'v' :
	      line_data.linebuf1[lnum   ] = ' ' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
	    case 'V' :
	      line_data.linebuf1[lnum   ] = ' ' ;
	      line_data.linebuf2[lnum ++] = ' ' ;
	      break;
       }
       if (mar_j<= 1 ) {
	   mcx[0]=revcode[0];
	   mcx[1]=revcode[1];
	   mcx[2]=revcode[2];
	   mcx[3]=revcode[3];
	   /*
	      printf("NU NAAR ddd() mmmm ! :");
	      mc = getchar();
	      ddd();
	      if ( mc == '#') exit(1);
	    */

       }
       switch (strt) {
	   case 1 :
	      if (mar_j > 1 ) {
		 for (mar_k=0; mar_k<4; mar_k++)
		    cop[ncop++] = revcode[mar_k];
	      }
	      break;
	   case 2 :
	   case 0 :
	      for (mar_k=0; mar_k<4; mar_k++)
		 cop[ncop++] = revcode[mar_k];
	      break;
       }
    }


    /*
	dit gaat naar de aanroepende functions
	if (line_data.vs > 0 ) {
	   if ( strt == 0 ) {
	      if (line_data.vs == 1) line_data.last = 0;
	      line_data.vs --;
	   }
	}

    */



    line_data.wsum    += length;
    line_data.line_nr =  lnum;
    end_line = strt;

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

     for ( fill_i = 2 ; fill_i<100 ;fill_i++ ) verdeelstring[fill_i]=0;

     idelta = u ;

     fill_casus = 0;
     if (idelta >=3 ) fill_casus ++;
     if (idelta >=8 ) fill_casus ++;
     if (idelta >=17) fill_casus ++;
     if (idelta >=24) fill_casus ++;

     switch (fill_casus)
     {
	case 0 :
	   if (line_data.nspaces == 0 ) /* no variable spaces */
	   {
	      if ( line_data.nfix > 0 ) {  /* fixed spaces */
		 verdeelstring[fill_n++] = ( datafix.u2 > 9 ) ?
			 datafix.u2 + 'a'-10 : datafix.u2 + '0';
		 verdeelstring[fill_n++] = ( datafix.u1 > 9 ) ?
			 datafix.u1 + 'a'-10 : datafix.u1 + '0';
	      } else {          /* neither kind of spacing */
		 verdeelstring[0]='8'; /* nothing */
		 verdeelstring[1]='3';
	      }
	   } else {       /* variable spaces  */
	      if ( idelta < 0 ) {

		 if ( line_data.nspaces * 2 < iabsoluut(idelta) ) {
		    printf("line too wide fill()\n");
		    printf("idelta%4d vars %3d ",idelta,line_data.nspaces);
		    getchar();
		    exit(1);
		    /* the adjustment wedges cannot cope with this */
		    /* minimum correction = 1/1 = -.0185" */
		 } else { /*  2 svp > iabs( idelta )
		       the adjustment wedges can still cope with this
		       situation, result a flat line...
			   */
		    calc_kg ( line_data.nspaces );
		    store_kg( );

		 }
	      } else {
		 calc_kg ( line_data.nspaces );
		 store_kg( );
	      }
	   }
	   break;
	case 1 :  /* >=4 <= 8  idelta == positive */
	   if ( line_data.nspaces < 3 ) {
	      var = 1;
	      adjust    ( wig[0], (float) (idelta-5)/(float) (1+line_data.nspaces) );
	      store_kg( );
	      verdeelstring[2] = 'v' ; /* GS1 */
	   } else {
	      calc_kg ( line_data.nspaces );
	      store_kg( );
	   }
	   break;
	case 2 :  /* > 8 <= 17 */
	   if ( line_data.nspaces < 3 ) {
	      radd = idelta - 9 ;
	      var = 1;
	      adjust( wig[4], ( (float) radd) / ( (float) (var+line_data.nspaces) ) );
	      store_kg( );
	      verdeelstring[2] = 'V' ; /* GS5 */
	   } else { /* flat filled line */
	      calc_kg ( line_data.nspaces );
	      store_kg( );
	   }
	   break;
	case 3 :  /* > 17 < 24 */
	   if ( line_data.nspaces < 3 ) {
	      radd = idelta - 18 ;
	      var = 2;
	      adjust ( wig[4], ((float) radd)/ ((float)(var+line_data.nspaces) ) );
	      store_kg( );
	      verdeelstring[2] = 'V' ; /* GS5 */
	      verdeelstring[3] = 'V' ;
	   } else {  /* flat filled line */
	      calc_kg ( line_data.nspaces );
	      store_kg( );
	   }
	   break;
	case 4 :  /* >= 24 */
	   var = 3;
	   qadd = idelta / 9;
	   radd =  ( idelta >=  27  ) ? idelta % 9 : idelta - 27 ;
	   adjust ( wig[4], ((float) radd)/((float) (var+line_data.nspaces) ) );
	   store_kg( );
	   fill_n = verdeel( );
	   if ( (line_data.nfix > 0) && (line_data.nspaces == 0) ) {
		 verdeelstring[fill_n++] = ( datafix.u2 > 9 ) ?
			 datafix.u2 + 'a'-10 : datafix.u2 +'0';
		 verdeelstring[fill_n++] = ( datafix.u1 > 9 ) ?
			 datafix.u1 +'a' -10 : datafix.u1 +'0';
	   }
	   break;
     }
}  /* fill_line  */





