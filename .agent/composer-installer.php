<?php

declare(strict_types=1);

/**
 * Composer Skills Installer
 *
 * Creates a symlink from .agent/skills to vendor/sickn33/antigravity-awesome-skills/skills
 * Run automatically via Composer post-install/post-update hooks.
 */

$vendorSkillsPath = './vendor/sickn33/antigravity-awesome-skills/skills';
$targetSkillsPath = './skills';

// Check if vendor package exists
if (!is_dir($vendorSkillsPath)) {
    echo "Skills package not found in vendor. Skipping skills installation.\n";
    exit(0);
}

// Remove existing symlink or directory
if (is_link($targetSkillsPath)) {
    unlink($targetSkillsPath);
    echo "Removed existing symlink at .agent/skills\n";
} elseif (is_dir($targetSkillsPath)) {
    echo "Warning: .agent/skills exists as a directory instead of a symlink.\n";
    echo "To fix this, run: rm -rf .agent/skills && composer run install-skills\n";
    exit(0);
}

// Create symlink to the skills subdirectory
if (symlink($vendorSkillsPath, $targetSkillsPath)) {
    echo "Created symlink: .agent/skills -> {$vendorSkillsPath}\n";
    echo "Skills installation complete!\n";
} else {
    echo "Error: Failed to create symlink.\n";
    exit(1);
}
