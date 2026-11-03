// positive_06.cpp
int g_counter = 5;

struct Reader
{
    int read()
    {
        return g_counter;
    }
};

int main()
{
    Reader r;
    return r.read();
}
