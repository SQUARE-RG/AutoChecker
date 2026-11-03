#define INDEX int // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-2]

int main()
{
    INDEX i = 0;
    i = i + 1;
    return i;
}
