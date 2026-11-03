// negative_04.cpp

int scan(long total)
{
    for (long i = 0; i < total; ++i)
    {
        if (i % 2 == 0)
        {
            switch (i) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-3]
            {
            }
        }
    }
    return 0;
}

int main()
{
    return scan(4);
}
