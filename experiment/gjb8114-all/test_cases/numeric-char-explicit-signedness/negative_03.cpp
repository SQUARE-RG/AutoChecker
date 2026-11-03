char globalValue = 10; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-20]

int main(void)
{
    int result = globalValue + 5;
    return result;
}
