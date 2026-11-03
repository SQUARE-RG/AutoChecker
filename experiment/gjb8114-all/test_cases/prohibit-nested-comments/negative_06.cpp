enum Color
{
    RED,
    // CHECK-MESSAGES: :[[@LINE+3]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-6]
    /*
    comment between enumerators
    /* nested enumerator comment
    still comment text
    */
    GREEN,
    BLUE
};

int main()
{
    return static_cast<int>(GREEN);
}
