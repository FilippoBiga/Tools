#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mach-o/loader.h>
#include <mach-o/fat.h>

// some code has been borrowed from http://reverse.put.as
// gcc -o nomodinit{,.c} -std=c99

int main(int argc, const char *argv[])
{
    FILE *inFile = NULL;
    FILE *outputFile = NULL;
    uint8_t *targetBuffer = NULL;
    uint32_t fileSize = 0;
    uint32_t magic = 0;
    char extension[] = ".patched";
    uint8_t *address = NULL;
    uint32_t nrLoadCmds = 0;
    struct load_command *loadCommand = NULL;
    char *outputName = NULL;
    uint32_t outputNameSize = 0;
    
    inFile = fopen(argv[1], "r");
    if (!inFile)
    {
        return 1;
    }
    
    fseek(inFile, 0L, SEEK_END);
    fileSize = ftell(inFile);
    fseek(inFile, 0L, SEEK_SET);
    
    targetBuffer = (uint8_t*)malloc(fileSize);
    fread(targetBuffer, fileSize, 1, inFile);
    
    fclose(inFile);
    
    magic = *(uint32_t*)(targetBuffer);    
    
    switch (magic)
    {
        case MH_MAGIC:
        {
            struct mach_header *machHeader = (struct mach_header*)(targetBuffer);
            nrLoadCmds = machHeader->ncmds;
            address = targetBuffer + sizeof(struct mach_header);
            
            break;
        }
            
        case MH_MAGIC_64:
        {
            struct mach_header_64 *machHeader = (struct mach_header_64*)(targetBuffer);
            nrLoadCmds = machHeader->ncmds;
            address = targetBuffer + sizeof(struct mach_header_64);
            
            break;
        }
        case FAT_CIGAM:
        {
            printf("Fat archives not supported.\n");
            free(targetBuffer);
            return 1;
        }

        default:
        {
            printf("Not a valid mach-o binary!\n");
            free(targetBuffer);
            return 1;
        }
    }
    
    for (uint32_t i = 0; i < nrLoadCmds; i++)
    {
        loadCommand = (struct load_command*)address;
        switch (loadCommand->cmd)
        {
            case LC_SEGMENT:
            {
                struct segment_command *segmentCommand = (struct segment_command *)(loadCommand);
                struct section *sectStart = (struct section *)((uint8_t*)segmentCommand + sizeof(struct segment_command));
                struct section *sectEnd = &sectStart[segmentCommand->nsects];
                
                struct section *section = NULL;
                for (section = sectStart; section < sectEnd; section++)
                {
                    if ((section->flags & SECTION_TYPE) == S_MOD_INIT_FUNC_POINTERS)
                    {
                        section->flags = SECTION_TYPE | S_REGULAR;
                    }
                }
                
                break;
            }
                
                
            case LC_SEGMENT_64:
            {
                struct segment_command_64 *segmentCommand = (struct segment_command_64 *)(loadCommand);
                struct section_64 *sectStart = (struct section_64 *)((uint8_t*)segmentCommand + sizeof(struct segment_command_64));
                struct section_64 *sectEnd = &sectStart[segmentCommand->nsects];
                
                struct section_64 *section = NULL;
                for (section = sectStart; section < sectEnd; section++)
                {
                    if ((section->flags & SECTION_TYPE) == S_MOD_INIT_FUNC_POINTERS)
                    {
                        section->flags = SECTION_TYPE | S_REGULAR;
                    }
                }
                
                break;
            }
        }
        
        address += loadCommand->cmdsize;
    }
    
    
    outputNameSize = strlen(argv[1]) + strlen(extension) + 1;
    outputName = malloc(outputNameSize);
    
    strncpy(outputName, argv[1], strlen(argv[1])+1);
    strncat(outputName, extension, sizeof(extension));
    outputName[outputNameSize-1] = '\0';
    
    outputFile = fopen(outputName, "wb");
    if (!outputFile)
    {
        free(outputName);
        free(targetBuffer);
        return 1;
    }
    
    if (fwrite(targetBuffer, fileSize, 1, outputFile) < 1)
    {
        printf("Write failed!\n");
        free(outputName);
        fclose(outputFile);
        free(targetBuffer);
        return 2;
    }
    
    
    printf("Done.\n");

    free(outputName);
    fclose(outputFile);
    free(targetBuffer);
    
    return 0;
}
