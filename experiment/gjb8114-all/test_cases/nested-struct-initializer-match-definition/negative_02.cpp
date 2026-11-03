struct Data
{
    unsigned int id;
    struct Pair
    {
        unsigned int values[2];
        unsigned int flag;
    } pair;
};

int main(void)
{
    struct Data data = {1, 2, 3, 4}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-3]
    return (0);
}
