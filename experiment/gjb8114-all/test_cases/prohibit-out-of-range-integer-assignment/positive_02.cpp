int main()
{
    unsigned char min_uchar = 0;
    unsigned char max_uchar = 255;
    signed char min_schar = -128;
    signed char max_schar = 127;
    unsigned int max_uint = 4294967295u;
    int min_int = -2147483647 - 1;

    long long total = static_cast<long long>(min_uchar) + max_uchar + min_schar + max_schar
                    + static_cast<long long>(max_uint) + min_int;

    return (total == 0) ? 0 : 1;
}
