
struct rccoord oldpos;
int gl_i;


int getlineAO()
{

    gli=0;
    do {
       glc = getche();
    }
       while (glc < 'A' || glc > 'O' );
    line_buffer[gli++]=glc;
    do {
       glc = getche();
    }
       while ( glc != '\0' && (glc < 'A' || glc > 'O' ));
    if (glc != '\0' ) {
       line_buffer[gli++]=glc;
    } else
       line_buffer[gli] = '\0';
    return ( gli);
}

int getline10()
{

    gli=0;
    do {
       glc = getche();
    }
       while (glc < '1' || glc > '0' );

    line_buffer[gli++]=glc;
    do {
       glc = getche();
    }
       while ( glc != '\0' && (glc < 'A' || glc > 'O' ));
    if (glc != '\0' ) {
       line_buffer[gli++]=glc;
    } else
       line_buffer[gli] = '\0';
    return ( gli);
}

int get_line()
{
   gl_i=0;

   for (gl_i=0;gl_i<25; gl_i++) line_buffer[gl_i]='\0';
   gl_i=0;

   /*
   if (try_x > 2) {

       ccc = getche();
       line_buffer[gli++]=ccc;
       glc = getche();
       while (! kbhit());

   }
    */

   while ( --gllim >0 && ( glc=getchar())!= EOF &&
		glc != '\n'&& gl_i<MAX-2)   line_buffer[gli++]= glc;
   if (glc =='\n')
       line_buffer[gli++]= glc;
   line_buffer[gli]='\0';


   return(gl_i);
}


