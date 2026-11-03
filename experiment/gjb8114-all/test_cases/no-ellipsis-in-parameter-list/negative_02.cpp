class Logger {
public:
    void write(const char* format, ...); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-15]
};

int main()
{
    return 0;
}
