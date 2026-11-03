namespace sample {
typedef unsigned int count_t;
}

int main()
{
    typedef double ratio_t;

    sample::count_t c = 1u;
    ratio_t r = 0.5;

    return static_cast<int>(c + r);
}
