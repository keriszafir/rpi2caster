#include <conio.h>
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdlib.h>

main()
{
    double set, width;
    set = 11.5;
    width = 80*9*set/1296;
    printf("Width =%12.6f inch",width);
    getchar();
    width = width /.1776;
    printf("width = %12.6f cicero",width);
    getchar();
}


