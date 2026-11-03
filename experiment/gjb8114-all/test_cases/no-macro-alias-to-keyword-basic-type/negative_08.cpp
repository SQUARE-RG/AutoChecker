#define CHARACTER char // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-2]

int main()
{
    CHARACTER letter = 'A';
    (void)letter;
    return 0;
}
