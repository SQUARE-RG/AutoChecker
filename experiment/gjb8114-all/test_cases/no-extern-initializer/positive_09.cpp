namespace cfg {
extern int limit;
int limit = 10;
}

int main()
{
    cfg::limit = 20;
    return cfg::limit;
}
