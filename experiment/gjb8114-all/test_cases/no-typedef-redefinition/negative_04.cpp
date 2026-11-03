struct Outer {
    typedef long id_type;

    struct Inner {
        typedef double id_type; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-3]
        id_type value;
    };

    id_type id;
};

int main()
{
    Outer o;
    o.id = 1L;
    Outer::Inner i;
    i.value = 2.5;
    return 0;
}
