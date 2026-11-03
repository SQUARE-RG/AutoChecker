void log_message(const char*); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-13]

void log_message(const char* msg)
{
    (void)msg;
}

int main()
{
    log_message("hello");
    return 0;
}
