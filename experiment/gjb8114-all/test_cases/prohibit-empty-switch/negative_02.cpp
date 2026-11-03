enum class Color
{
    red,
    green
};

struct Handler
{
    void handle(Color c)
    {
        switch (c)
        {
        } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-3]
    }
};

int main()
{
    Handler h;
    h.handle(Color::red);
    return 0;
}
