struct Decoder
{
    static void decode(unsigned short code)
    {
        switch (code) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-3]
        {
            // Empty handler set.
        }
    }
};

int main()
{
    Decoder::decode(0);
    return 0;
}
