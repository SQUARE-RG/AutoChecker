// negative_06.cpp
int g_counter = 5;

struct Reader
{
    int read()
    {
        extern int g_counter; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-17]
        return g_counter;
    }
};

int main()
{
    Reader r;
    return r.read();
}
