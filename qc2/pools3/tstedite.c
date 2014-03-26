/* c:\qc2\pools3\tsteditE.c */




void test_tsted( void )
{
    char tc, *pc, tl, ant ;
    int firstline , crr ;
    char ans, ansi ;
    int tmax, ti;

    char tst_buff[500];

    aantal_lines = 0;

    firstline = 0;
    regel_tootaal = 0;

    clear_linedata();

    kind           = 0 ;
    line_data.last = 0.;
    line_data.vs   = 0 ;
    line_data.addlines = 0;
    line_data.add  = 0 ;
    line_data.nlig = 3 ;
    line_data.para = 0 ;
    line_data.c_style = 0; /* default current style */


    cls();
    ans = 'n';
    do {
       printf("read matrix-file ? <y/n> ");
       tl  = get_line();
       ans = line_buffer[0];

       switch (ans){
	  case 'j' :
	  case 'J' :
	  case 'y' :
	  case 'Y' :
	     ans = 'y';
	     break;
	  case 'N' :
	     ans = 'n'; break;
	  case 'n' : break;
	  default  :
	     ans = ' '; break;
       }
    }
       while ( ans == ' ');

    if ( ans == 'y' ) read_mat();

    displaym();

    for (tst_i=0; tst_i< MAXBUFF; tst_i++)
       readbuffer[tst_i] = '\0'; /* at the beginning this is empty */
    nreadbuffer = 0;
    ntestbuf = 0;

    inpathtext[0]='\0';
    inpathtext[1]='\0';

    cls();
    printf("Give name textfile \n\n");
    read_inputname();


    strcpy (outpathcod, inpathtext );
    _splitpath( outpathcod, drive, dir, fname, ext );
    strcpy( ext, "cod");
    _makepath ( outpathcod, drive, dir, fname, ext );

    if( ( foutcode = fopen( outpathcod, "w+" )) == NULL )
    {
	printf("output failure" );
	exit( 1 );
    }

    strcpy (outpathtext, inpathtext );
    _splitpath( outpathtext, drive, dir, fname, ext );
    strcpy( ext, "tx2");
    _makepath ( outpathtext, drive, dir, fname, ext );

    if( ( fouttext = fopen( outpathtext, "w+" )) == NULL )
    {
	printf("output failure" );
	exit( 1 );
    }

    crp_fread  = 0;
    filewijzer = 0;
    nreadbuffer=0;

    mcx[0] = 0x4c; /* NKJ    */
    mcx[1] = 0x04; /* g     */
    mcx[2] = 0x00;
    mcx[3] = 0x01; /* k     */
    mcx[4] = 0x7f; /* end of file sign */
    store_code();
    mcx[0] = 0x0;  /* # extra square lets the machine stop */
    mcx[1] = 0x0;  mcx[2] = 0x0;  mcx[3] = 0x0;
    mcx[4] = 0x0f; /* separator */
    store_code();
    datafix.wsp   =  6  ;  /* default value = 6 points */
    central.fixed = 'y' ;
    fixed_space();


    EOF_f = 0;

    do {
	/* first:  tested  9 march 2006
	   read until ^Cx is met
	   read commands in first line

	   */

	/* decode paragraph first
	   don't read when ^Cx is at the end of the buffer
	   but empty readbuffer first
	   */

	crr = 0;
	/* printf("place 1 : nrb = %3d ",nreadbuffer); */

	if ( nreadbuffer > 3 ) {
	    if ( readbuffer[nreadbuffer-3] == '^' &&
		 readbuffer[nreadbuffer-2] == 'C' ) crr = 1;
	}
	/*
	if (crr == 1 ) {
	   printf("crr = 1 rb[nrb-3/-2] = %1c %1c ",
		 readbuffer[nreadbuffer-3],
		 readbuffer[nreadbuffer-2]  ) ;
	} else {
	   printf("crr = 0                        ");
	}
	printf("\n");
	*/
	/*
	if (crr == 1 ) { printf("no reading ");
			 if (getchar()=='#') exit(1);
	}
	 */

	if (crr == 0 ) {
	  /*  printf("place 2: naar leesregel nrb = %3d \n" , nreadbuffer ); */
	    leesregel();
	  /*  printf("place 3: Na leesregel   nrb = %3d", nreadbuffer ); */
	}

	   /* else {
		 printf("place 4: no reading from file ");
	      }
	      if (getchar()=='#') exit(1);
	   */

	if (firstline == 0 ) {    /* handle commands first line */
	   switch (readbuffer[0] ) {
	      case '^' :
	      case '@' :
		if ( readbuffer[1] == 'B' ) {
		    first();
		    nreadbuffer =0;
		    for (tst_i=atel; tst_i< BUFSIZ ; tst_i ++)
			   readbuffer[tst_i] = '\0';
		    leesregel();
		}
		break;
	   }
	   disp_attrib();

	   firstline = 1;
	}

	test_EOF();

	if ( EOF_f == 0 )
	{
	   /* disp_line(); */

	   do {
	      outb_n = 0;
	      outtextbuffer[0]='\0';
	      outtextbuffer[1]='\0';

	      tst_used = testzoek5 ( ) ;

	      /*
	      printf("na testzoek5 ");
	      if (getchar()=='#') exit(1);
	       */

	      /*
	       int      outb_n                  / * aantal chars in outtextbuffer * /
	       FILE     *fouttext;              / * pointer text output-file * /
		char     outpathtext[_MAX_PATH]; / * name text-file * /
		char     outtextbuffer[BUFSIZ];  / * buffer reading from text-file  * /
	      */


	      print_at(14,0,"");

	      for ( ti=0; ti < outb_n ; ti++) {
		if (outtextbuffer[ti])
		       printf("%1c",outtextbuffer[ti]);
	      }


	     /*
	      printf("Na outbuffer t3j = %3d ",t3j);
	      if (getchar()=='#') exit(1);
	      */

	      print_at(7,0,"");

	      /* vertaalde regel afdrukken op scherm */

	      tmax =0;
	      for ( ti=0; ti < t3j ; ti++) {
		if ( readbuffer[ti]=='^') {
		    ti+=2;
		} else {
		    if (readbuffer[ti]) printf("%1c",readbuffer[ti]);
		}
		tmax++;
		if (tmax>350) { printf("tmax = %3d ti %3d t3j =%3d ",
				     tmax, ti, t3j );
		   if (getchar()=='#') exit(1);
		}
	      }

	      /* readbuffer copieren
		 naar tx2-file schrijven....

	       */


	      print_at(20,1,"");
	      printf("line %4d in buffer %3d chars used %3d vars = %3d just = %2d/%2d ",
		      aantal_lines+1,nreadbuffer, tst_used,
		      line_data.nspaces, line_data.u1, line_data.u2 );

	      /* printf("vars = %3d ",line_data.nspaces ); */
	      do {
		 print_at(22,1," accept =  retry \\           ");
		 print_at(22,22,"");
		 /*
		    line_buffer[0] = '\0' ;
		    line_buffer[1] = '\0' ;
		    tl  = get_line();
		    ant = line_buffer[0];
		 */
		 ant = getche();
		 if (ant =='#') exit(1);


	      }
		 while (ant != '=' && ant != '\\' && ant != ']' &&
			ant != '1' && ant != '2'  && ant != '3' &&
			ant != '4' );
	      ans = ant;
	      switch (ans) {
		 case ']' : ant = '='; ansi = 0; break;
		 case '1' : ant = '='; ansi = 1; break;
		 case '2' : ant = '='; ansi = 2; break;
		 case '3' : ant = '='; ansi = 3; break;
		 case '4' : ant = '='; ansi = 4; break;
		 /*
		  hier kunnen nog meer varianten komen...

		  */
		 default  : ans = ' '; ansi = 0; break;

	      }
	   }
	      while ( ant != '=');


	   atel = 0;
	   aantal_lines ++;

	   switch (ans) {
	      case ']' :
		 tst_buff[atel++]='^';tst_buff[atel++]='a';tst_buff[atel++]='e';
		 tst_buff[atel++]='^';tst_buff[atel++]='+';tst_buff[atel++]='2';
		 ans = ' ';
		 break;
	      /*
	       hier kunnen nog meer varianten komen

	       */
	   }
	   if (ansi > 0) {
	      tst_buff[atel++]='^';tst_buff[atel++]='F';tst_buff[atel++]='c';
	      for (tst_i = 0; tst_i < ansi ; tst_i++){
		 tst_buff[atel++]='_';
		 tst_buff[atel++]='_';
	      }
	   }



	   if (nreadbuffer > tst_used ) {

	      /* move remainder buffer to the front */

	      if (readbuffer[tst_used] == ' ') tst_used ++;

	      for (tst_i = tst_used; tst_i < nreadbuffer ; tst_i++) {
		 ctst = readbuffer[tst_i];
		 switch ( ctst) {
		    case '\015': break;
		    case '\012': break;
		    default    :
			       /* printf("%1c",ctst); */
		       tst_buff[atel++] = ctst; /* readbuffer[atel++] = ctst; */
		       break;
		 }
	      }
	   }
	   for (tst_i = 0; tst_i < atel ; tst_i++) {
	      readbuffer[tst_i] = tst_buff[tst_i];
	   }

	   nreadbuffer = atel;   /* adjust nreadbuffer */

	   for (tst_i=atel; tst_i< BUFSIZ ; tst_i ++)
	       readbuffer[tst_i] = '\0'; /* clear rest readbuffer */

	   store_text(0);


	   for (tst_i=0; tst_i < ncop ; ) {
	       mcx[0] = cop[tst_i ++];
	       mcx[1] = cop[tst_i ++];
	       mcx[2] = cop[tst_i ++];
	       mcx[3] = cop[tst_i ++];
	       store_code();
	       if (caster == 'k' ) { /* to interface */
		    zendcodes();
	       }


		 /* hier testen of er een variable spatie gebruikt wordt
		    de uitvulling is mu1 / mu2
		    eerst testen of er een uitvulling staat

		 * /
		 if ( test_GS( mcx[1] ) ) {
		     / * printf(" GS gevonden \n"); * /
		     / * testen of er ook een uitvulling staat
			 dan mag die niet veranderd worden ....
		       * /
		    if ( cop[tst_i] == 0x48 ) { / * NK * /
		    / *  printf("vaste spatie gevonden ");
			 printf("Nu geen extra code inpassen\n");
		      * /
		    } else {
		       / *
		       switch ( mcx[2] ) {
			  case 0x40 :
			     printf("GS1 %2d/%2d",mu1,mu2);
			     break;
			  case 0x20 :
			     printf("GS2 %2d/%2d",mu1,mu2);
			     break;
		       }
			 * /
		       switch ( mcx[2] ) {
			  case 0x40 :
			  case 0x20 :
			     mcx[0] = 0x48;  / * NK * /
			     mcx[1] = 0x24;  / * S 0075 * /
			     mcx[2] = 0;
			     mcx[3] = 0;
			     setrow( mcx , mu1 );
			     store_code();
			     if (caster == 'k' ) { zendcodes(); }
			     mcx[0] = 0x44;  / * NJ * /
			     mcx[1] = 0x20;  / * S * /
			     mcx[2] = 0;
			     mcx[3] = 0x01;
			     setrow( mcx, mu2 );
			     store_code();
			     if (caster == 'k' ) { zendcodes(); }
			     break;
		       }
		    }
		    / * if (getchar()=='#') exit(1); * /


	       }

		 / * laatste toevoeging
		     eindigt hier
		 */

	   }


	} /* einde if EOF_f != 0  */


	if ( feof ( fintext) ) {

	    /*

	    ^EF wegschrijven naar output-textfile

	    printf("\n end of file reached nrb %3d ",nreadbuffer);
	    if (getchar()=='#') exit(1);
	     */

	    if ( nreadbuffer == 0 ) EOF_f = 1;
	}

    }
	while ( ! EOF_f );  /* 23=juni 2006 */
    /*
    printf("Nu gaan wegschrijven ");
    if (getchar()=='#') exit(1);
     */

    outtextbuffer[0 ]  = '^';
    outtextbuffer[1 ]  = 'E' ;
    outtextbuffer[2 ]  = 'F' ;
    outtextbuffer[3 ]  = 10 ;
    outtextbuffer[4 ]  = 12 ;
    outtextbuffer[5 ]  = '\0';
    outb_n = 5;
    store_text(1);

    fclose ( fintext);
    fclose ( foutcode);
    fclose ( fouttext);

    printf("\nfile ");
    for ( ti=0;inpathtext[ti] != '\0'; ti++)
      printf("%1c",inpathtext[ti]);

    printf(" contains %3d lines ",aantal_lines);

    if (getchar()=='#') exit(1);

    /* ans */
}


