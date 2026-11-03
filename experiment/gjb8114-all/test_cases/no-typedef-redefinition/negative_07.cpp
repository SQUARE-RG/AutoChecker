typedef int GlobalInt;

void functionScope()
{
    typedef double OuterLocal;
    struct LocalClass
    {
        typedef long OuterLocal; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-3]
        OuterLocal value;
    };

    LocalClass obj;
    obj.value = 1;
}

int main()
{
    functionScope();
    return 0;
}
