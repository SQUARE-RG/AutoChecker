/*
    File-scope comment begins here.
    Next line contains a nested block comment opener.
    /* // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-6]
    The nested opener is ignored by the lexer; the following line closes the outer comment.
*/
int main()
{
    return 0;
}
