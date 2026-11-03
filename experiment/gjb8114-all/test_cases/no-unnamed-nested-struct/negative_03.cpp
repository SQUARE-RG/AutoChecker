struct RegisterMap
{
    unsigned int id;
    struct StatusBits
    {
        unsigned int ready : 1;
        unsigned int error : 1;
    }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-9]
};

int main()
{
    RegisterMap map{};
    map.id = 1U;
    return 0;
}
