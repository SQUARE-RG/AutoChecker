#include <stdlib.h>
#include <string.h>

struct Department {
    int dept_id;
    char dept_name[50];
};

struct Company {
    int company_id;
    struct Department *dept;
};

void test_complex_struct(void) {
    struct Company *comp = (struct Company*)malloc(sizeof(struct Company));
    if (comp != NULL) {
        comp->dept = (struct Department*)malloc(sizeof(struct Department));
        if (comp->dept != NULL) {
            comp->dept->dept_id = 101;
            strcpy(comp->dept->dept_name, "Engineering");
            
            free(comp->dept);
            comp->dept = NULL;  // 符合：嵌套结构体内存正确释放置空
        }
        free(comp);
        comp = NULL;  // 符合：外层结构体也正确置空
    }
}

int main(void) {
    test_complex_struct();
    return 0;
}