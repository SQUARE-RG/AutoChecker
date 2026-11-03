class Config {
public:
    signed int flag : 3;
    signed int level : 4;
};

int main(void)
{
    Config cfg;
    cfg.flag = -1;
    cfg.level = 3;
    return 0;
}
