int main()
{
    int i = 0;
    unsigned int limit = 3;
    do
    {
        ++i;
    } while (i != limit); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-5]
    return i;
}
