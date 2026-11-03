typedef int SINT_32;
typedef unsigned int UINT_32;

class Config {
public:
    UINT_32 count;
    SINT_32 level;
};

SINT_32 main() {
    Config config{1U, 0};
    return static_cast<SINT_32>(config.count) + config.level;
}
