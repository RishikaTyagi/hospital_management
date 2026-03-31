#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_LINE 256
#define MAX_PATIENTS 1000

typedef struct {
    int id;
    char name[100];
    int age;
    char gender[10];
    char phone[20];
    char dept[50];
    int severity;
} Patient;

int is_numeric(const char *str) {
    if (str == NULL || *str == '\0') return 0;
    for (int i = 0; str[i] != '\0'; i++) {
        if (!isdigit((unsigned char)str[i])) return 0;
    }
    return 1;
}

int is_valid_dept(const char *dept) {
    const char *valid_depts[] = {"Cardiology", "Neurology", "Orthopedics", "Pediatrics", "General"};
    int num_depts = sizeof(valid_depts) / sizeof(valid_depts[0]);
    for (int i = 0; i < num_depts; i++) {
        if (strcmp(dept, valid_depts[i]) == 0) return 1;
    }
    return 0;
}

int get_next_id() {
    FILE *f = fopen("id_tracker.txt", "r");
    int id = 1;
    if (f != NULL) {
        fscanf(f, "%d", &id);
        fclose(f);
    }
    FILE *fw = fopen("id_tracker.txt", "w");
    if (fw != NULL) {
        fprintf(fw, "%d", id + 1);
        fclose(fw);
    }
    return id;
}

void parse_patient(char *line, Patient *p) {
    char *token = strtok(line, "|");
    if(token) p->id = atoi(token);
    
    token = strtok(NULL, "|");
    if(token) strncpy(p->name, token, sizeof(p->name)-1);
    
    token = strtok(NULL, "|");
    if(token) p->age = atoi(token);
    
    token = strtok(NULL, "|");
    if(token) strncpy(p->gender, token, sizeof(p->gender)-1);
    
    token = strtok(NULL, "|");
    if(token) strncpy(p->phone, token, sizeof(p->phone)-1);
    
    token = strtok(NULL, "|");
    if(token) strncpy(p->dept, token, sizeof(p->dept)-1);
    
    token = strtok(NULL, "|");
    if(token) p->severity = atoi(token);
}

void format_patient(char *buffer, Patient *p) {
    sprintf(buffer, "%d|%s|%d|%s|%s|%s|%d\n", p->id, p->name, p->age, p->gender, p->phone, p->dept, p->severity);
}

void insert_emergency(Patient new_p) {
    Patient patients[MAX_PATIENTS];
    int count = 0;
    FILE *f = fopen("emergency_queue.txt", "r");
    if (f != NULL) {
        char line[MAX_LINE];
        while (fgets(line, sizeof(line), f)) {
            line[strcspn(line, "\n")] = 0; // Remove newline
            if (strlen(line) > 0) {
                parse_patient(strdup(line), &patients[count]);
                count++;
            }
        }
        fclose(f);
    }

    // Insert as priority queue (higher severity first)
    int insert_idx = count;
    for (int i = 0; i < count; i++) {
        if (new_p.severity > patients[i].severity) {
            insert_idx = i;
            break;
        }
    }

    // Shift elements
    for (int i = count; i > insert_idx; i--) {
        patients[i] = patients[i - 1];
    }
    patients[insert_idx] = new_p;
    count++;

    // Write back
    f = fopen("emergency_queue.txt", "w");
    if (f != NULL) {
        char buffer[MAX_LINE];
        for (int i = 0; i < count; i++) {
            format_patient(buffer, &patients[i]);
            fputs(buffer, f);
        }
        fclose(f);
    }
}

void insert_normal(Patient new_p) {
    FILE *f = fopen("normal_queue.txt", "a");
    if (f != NULL) {
        char buffer[MAX_LINE];
        format_patient(buffer, &new_p);
        fputs(buffer, f);
        fclose(f);
    }
}

void do_register(int argc, char *argv[]) {
    if (argc != 8) {
        printf("ERROR: Missing arguments for registration\n");
        return;
    }
    char *name = argv[2];
    char *age_str = argv[3];
    char *gender = argv[4];
    char *phone = argv[5];
    char *dept = argv[6];
    char *severity_str = argv[7];

    if (strlen(name) == 0) {
        printf("ERROR: Name cannot be empty\n");
        return;
    }
    if (!is_numeric(age_str) || atoi(age_str) <= 0) {
        printf("ERROR: Invalid age\n");
        return;
    }
    if (!is_numeric(phone) || strlen(phone) < 7 || strlen(phone) > 15) {
        printf("ERROR: Invalid phone number\n");
        return;
    }
    if (!is_valid_dept(dept)) {
        printf("ERROR: Department does not exist\n");
        return;
    }
    if (!is_numeric(severity_str)) {
        printf("ERROR: Severity must be a number\n");
        return;
    }

    Patient p;
    p.id = get_next_id();
    strncpy(p.name, name, sizeof(p.name)-1); p.name[sizeof(p.name)-1]='\0';
    p.age = atoi(age_str);
    strncpy(p.gender, gender, sizeof(p.gender)-1); p.gender[sizeof(p.gender)-1]='\0';
    strncpy(p.phone, phone, sizeof(p.phone)-1); p.phone[sizeof(p.phone)-1]='\0';
    strncpy(p.dept, dept, sizeof(p.dept)-1); p.dept[sizeof(p.dept)-1]='\0';
    p.severity = atoi(severity_str);

    if (p.severity > 0) {
        insert_emergency(p);
        printf("SUCCESS: Patient registered to Emergency Queue with ID %d\n", p.id);
    } else {
        insert_normal(p);
        printf("SUCCESS: Patient registered to Normal Queue with ID %d\n", p.id);
    }
}

int pop_first(const char *filename, Patient *treated) {
    Patient patients[MAX_PATIENTS];
    int count = 0;
    FILE *f = fopen(filename, "r");
    if (f == NULL) return 0;
    
    char line[MAX_LINE];
    while (fgets(line, sizeof(line), f)) {
        line[strcspn(line, "\n")] = 0;
        if (strlen(line) > 0) {
            parse_patient(strdup(line), &patients[count]);
            count++;
        }
    }
    fclose(f);

    if (count == 0) return 0;

    *treated = patients[0];

    f = fopen(filename, "w");
    if (f != NULL) {
        char buffer[MAX_LINE];
        for (int i = 1; i < count; i++) {
            format_patient(buffer, &patients[i]);
            fputs(buffer, f);
        }
        fclose(f);
    }
    return 1;
}

void do_treat() {
    Patient treated;
    int found = pop_first("emergency_queue.txt", &treated);
    if (!found) {
        found = pop_first("normal_queue.txt", &treated);
    }
    
    if (found) {
        FILE *h = fopen("history.txt", "a");
        if (h != NULL) {
            char buffer[MAX_LINE];
            format_patient(buffer, &treated);
            fputs(buffer, h);
            fclose(h);
        }
        printf("TREATED: %d|%s|%d|%s|%s|%s|%d\n", treated.id, treated.name, treated.age, treated.gender, treated.phone, treated.dept, treated.severity);
    } else {
        printf("NONE: No patients in the queue\n");
    }
}

void print_queue(const char *filename, const char *label) {
    FILE *f = fopen(filename, "r");
    if (f == NULL) return;
    char line[MAX_LINE];
    while (fgets(line, sizeof(line), f)) {
        line[strcspn(line, "\n")] = 0;
        if (strlen(line) > 0) {
            printf("%s|%s\n", label, line);
        }
    }
    fclose(f);
}

void do_list() {
    print_queue("emergency_queue.txt", "EMERGENCY");
    print_queue("normal_queue.txt", "NORMAL");
}

int search_in_file(const char *filename, int id) {
    FILE *f = fopen(filename, "r");
    if (f == NULL) return 0;
    char line[MAX_LINE];
    while (fgets(line, sizeof(line), f)) {
        line[strcspn(line, "\n")] = 0;
        if (strlen(line) > 0) {
            Patient p;
            parse_patient(strdup(line), &p);
            if (p.id == id) {
                printf("FOUND: %d|%s|%d|%s|%s|%s|%d|(%s)\n", p.id, p.name, p.age, p.gender, p.phone, p.dept, p.severity, filename);
                fclose(f);
                return 1;
            }
        }
    }
    fclose(f);
    return 0;
}

void do_search(int argc, char *argv[]) {
    if (argc < 3 || !is_numeric(argv[2])) {
        printf("ERROR: Invalid ID\n");
        return;
    }
    int id = atoi(argv[2]);
    if (search_in_file("emergency_queue.txt", id)) return;
    if (search_in_file("normal_queue.txt", id)) return;
    if (search_in_file("history.txt", id)) return;
    printf("NOT FOUND: Patient ID %d does not exist in any record\n", id);
}

void do_history() {
    FILE *f = fopen("history.txt", "r");
    if (f == NULL) {
        return; // Empty history
    }
    char line[MAX_LINE];
    int count = 0;
    while (fgets(line, sizeof(line), f)) {
        line[strcspn(line, "\n")] = 0;
        if (strlen(line) > 0) {
            printf("%s\n", line);
            count++;
        }
    }
    fclose(f);
}

void do_clear_history() {
    FILE *f = fopen("history.txt", "w");
    if (f != NULL) {
        fclose(f);
        printf("SUCCESS: History cleared\n");
    } else {
        printf("ERROR: Could not clear history\n");
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("ERROR: No command provided\n");
        return 1;
    }
    
    char *cmd = argv[1];
    
    if (strcmp(cmd, "register") == 0) {
        do_register(argc, argv);
    } else if (strcmp(cmd, "treat") == 0) {
        do_treat();
    } else if (strcmp(cmd, "list") == 0) {
        do_list();
    } else if (strcmp(cmd, "search") == 0) {
        do_search(argc, argv);
    } else if (strcmp(cmd, "history") == 0) {
        do_history();
    } else if (strcmp(cmd, "clear_history") == 0) {
        do_clear_history();
    } else {
        printf("ERROR: Unknown command %s\n", cmd);
        return 1;
    }
    
    return 0;
}
