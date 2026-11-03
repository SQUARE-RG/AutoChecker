char* strerror(int errnum) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-1]
{
    static char message[] = "error";
    (void)errnum;
    return message;
}

int main()
{
    char* msg = strerror(1);
    (void)msg;
    return 0;
}
