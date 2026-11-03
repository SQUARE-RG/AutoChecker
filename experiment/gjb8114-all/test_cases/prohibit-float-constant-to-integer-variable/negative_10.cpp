int main()
{
    int* p = new int(6.75); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-1]
    int result = *p;
    delete p;
    return result;
}
