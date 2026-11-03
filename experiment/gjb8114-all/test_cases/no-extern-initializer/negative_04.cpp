struct Pair
{
    int first;
    int second;
};

extern Pair g_pair = {1, 2}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-19]

int main()
{
    return g_pair.first + g_pair.second;
}
