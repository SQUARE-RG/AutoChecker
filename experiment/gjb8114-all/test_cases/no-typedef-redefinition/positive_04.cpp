namespace Alpha {
    typedef int handle_t;
    handle_t make() { return 7; }
}

namespace Beta {
    typedef double handle_t;
    handle_t make() { return 2.5; }
}

int main()
{
    Alpha::handle_t a = Alpha::make();
    Beta::handle_t b = Beta::make();
    return (a == 7 && b > 2.0) ? 0 : 1;
}
