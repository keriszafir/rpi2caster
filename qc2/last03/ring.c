/*
   c:\qc2\last02\ring.c

   ring structuur van records


 */



void clean_voorraad()
{
    basis = & voorraad[1];

    voorraad[0].fname = 149;
    voorraad[0]._fore = & voorraad[149];

    for ( cl_i=0 ; cl_i<150 ; cl_i++) {

	for (cl_j=0;cl_j<4;cl_j++)
	   voorraad[cl_i]._lig[cl_j]= '\0';  /* glyph in the mat */

	voorraad[cl_i]._srt = 0;           /* kind of alphabet */
	voorraad[cl_i]._lwidth = 0.;       /* linewidth until this mat */
	voorraad[cl_i]._ncop = 0;          /* number of codes before   */
	voorraad[cl_i]._n_code;            /* number of codes infolved */

	for (cl_j=0;cl_j<40;cl_j++)
	    voorraad[cl_i]._code[cl_j] = 0xff;  /* actual code 10*4 max */

	voorraad[cl_i].name= cl_i;         /* record number */

	if (cl_i > 0 ) {
	   voorraad[cl_i]._fore = & voorraad[cl_i-1];  /* record before this rec */
	   voorraad[cl_i].fname = cl_i-1;
	}
	if (cl_i < 149 ) {
	   voorraad[cl_i]._next = & voorraad[cl_i+1];  /* record before this rec */
	   voorraad[cl_i].lname = cl_i+1;
	}
    }

    voorraad[149].lname = 0;
    voorraad[149]._next = & voorraad[0];


}

/*

    terug plaatsen record





 */



void start_rij ( void )
{
    r_basis = voorraad[0].lname;
    r_wijzer = r_basis;

    basis   = voorraad[0]._next ;

    voorraad[0].lname = voorraad[r_basis].lname;
    voorraad[0]._next = voorraad[r_basis]._next;

    voorraad[ voorraad[0].lname ].fname = 0;
    voorraad[ voorraad[0].lname ]._fore = & voorraad[0];

    voorraad[ r_basis].lname = -1;
    voorraad[ r_basis].fname = -1;

    voorraad[ r_basis]._fore = NIL;
    voorraad[ r_basis]._next = NIL;

}


int neem ( )
{
    int w, n, f;

    w = voorraad[0].lname;
    /* voorraad[0].lname = voorraad[w].lname; */

    voorraad[ voorraad[0].lname = voorraad[w].lname ].fname = 0;

    return ( w);
}

void achter ( int nr )
{
    voorraad[r_wijzer].lname = nr;
    voorraad[nr].fname = r_wijzer;
    voorraad[nr].lname = -1;
    r_wijzer = nr;
}



void tussen ( int nr , int ptr )
{
   ;
}

/* terug plaatsen van een record van de rij in de voorraad */

void terug( int nr )
{
     /* wijzer */




     voorraad[ voorraad[nr].fname ] .lname = voorraad[nr].lname;
     voorraad[ voorraad[nr].lname ] .fname = voorraad[nr].fname;

     for (cl_j=0;cl_j<4;cl_j++)
	voorraad[nr]._lig[cl_j]= '\0';  /* glyph in the mat */
     voorraad[nr]._srt = 0;      /* kind of alphabet */
     voorraad[nr]._lwidth = 0;        /* linewidth until this mat */
     voorraad[nr]._ncop = 0;           /* number of codes before   */
     voorraad[nr]._n_code=0;        /* number of codes infolved */

     for (cl_j=0;cl_j<40;cl_j++)
	voorraad[nr]._code[cl_j] = 0xff;  /* actual code 10*4 max */

     voorraad[nr].fname = 0;
     voorraad[nr]._fore = & voorraad[0] ;

     voorraad[nr].lname = voorraad[0].lname;
     voorraad[nr]._next = voorraad[0]._next ;

     voorraad[0].lname  = nr;
     voorraad[0]._next  = & voorraad[nr];

     voorraad[ voorraad[nr].lname ] . fname = nr;
     voorraad[ voorraad[nr].lname ] . _fore = & voorraad[nr];

}






void main_ring()
{
    int ri, ki;

    clean_voorraad();
    start_rij (  ) ;
    achter ( neem () );
    achter ( neem () );
    achter ( neem () );

    r_t1 = r_basis;


    printf("\n r_basis = %3d fore %3d next %3d \n",r_basis,
	   voorraad[ r_basis].fname , voorraad[ r_basis].lname );

    do {
       printf(" r_t1 %3d voor %3d na %3d \n",voorraad[r_t1].name,
	     voorraad[r_t1].fname,
	     voorraad[r_t1].lname);
       if (getchar()=='#') exit(1);


       if ( voorraad[r_t1].lname != -1 )
	   r_t1 = voorraad[r_t1].lname;
    }
       while ( voorraad[r_t1].lname != -1 );



       printf(" r_t1 %3d voor %3d na %3d ",voorraad[r_t1].name,
	     voorraad[r_t1].fname,
	     voorraad[r_t1].lname);
       if (getchar()=='#') exit(1);






    /*


    achter ( neem () );
    show();

    printf(" r_basis = %3d fore %3d next %3d \n",r_basis,
	   voorraad[ r_basis].fname , voorraad[ r_basis].lname );
    show2();


    */

    printf("Stoppen ");

    if (getchar()=='#') exit(1);


}

