
struct rccoord oldpos;


int gl_i;



int getlineAO()
{
    int gi;
    char gc;

    gi=0;
    do {
       gc = getche();
    }
       while (gc < 'A' || gc > 'O' );
    line_buffer[gi++]=gc;
    do {
       gc = getche();
    }
       while ( gc != '\0' && (gc < 'A' || gc > 'O' ));
    if (gc != '\0' ) {
       line_buffer[gi++]=gc;
    } else
       line_buffer[gi] = '\0';
    return ( gi);
}

int getline10()
{
    int gi;
    char gc;

    gi=0;
    do {
       gc = getche();
    }
       while (gc < '1' || gc > '0' );
    line_buffer[gi++]=gc;
    do {
       gc = getche();
    }
       while ( gc != '\0' && (gc < 'A' || gc > 'O' ));
    if (gc != '\0' ) {
       line_buffer[gi++]=gc;
    } else
       line_buffer[gi] = '\0';
    return ( gi);
}


int get_line()
{
   int ccc;

   gl_i=0;

   for (gl_i=0;gl_i<25; gl_i++) line_buffer[gl_i]='\0';
   gl_i=0;

   if (try_x > 2) {

       ccc=getche();
       line_buffer[gli++]=ccc;
       glc = getche();
       while (! kbhit());

   }


   while ( --gllim >0 && ( glc=getchar())!= EOF &&
		glc != '\n'&& gl_i<MAX-2)   line_buffer[gli++]= glc;
   if (glc =='\n')
       line_buffer[gli++]= glc;
   line_buffer[gli]='\0';


   return(gl_i);
}

