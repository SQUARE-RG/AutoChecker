typedef char RawChar;

int main()
{
    RawChar value = 10;
    int result = value * 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-20]
    return result;
}
